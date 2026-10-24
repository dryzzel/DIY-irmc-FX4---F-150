import importlib.util
import json
import os
import tempfile
import types
import unittest
from unittest.mock import patch


class VehicleTests(unittest.TestCase):
    def simulate(self, mode='normal'):
        clock = [0]
        plant_hall = [45000]
        duration = 30000 if mode == "rapid" else 4500
        pins = {}
        events = []
        class Pin:
            OUT = 1
            def __init__(self, n, *args, value=0):
                self.n, self.level = n, value
                pins[n] = self
            def value(self, value=None):
                if value is not None:
                    self.level = int(value)
                    events.append((clock[0], self.n, self.level))
                if self.n == 15:
                    if mode == "rapid": return (clock[0] // 1100) % 2
                    return int(clock[0] >= 2200) if mode == 'normal' else 0
                return self.level
            def on(self): self.value(1)
            def off(self): self.value(0)
        class ADC:
            def __init__(self, n): pass
            def read_u16(self):
                if mode == 'rapid':
                    if pins[5].level and pins[2].level != pins[3].level:
                        plant_hall[0] += 10 if pins[2].level else -10
                    return plant_hall[0]
                if mode == 'hall_error' and clock[0] >= 950: return 65535
                if mode == 'timeout': return 32000
                if clock[0] < 1000: return 32000
                return 45000 if clock[0] < 3300 else 20000
        class PWM:
            def duty_u16(self, x): pass
            def freq(self, x): pass
        class WDT:
            def __init__(self, timeout): pass
            def feed(self): pass
        def sleep(ms):
            clock[0] += ms
            if clock[0] >= duration + 200: raise KeyboardInterrupt
        hw = types.SimpleNamespace(DIRECCION_A=1, TOPE_A=40000, TOPE_B=26000,
            RETENCION_A=35000, RETENCION_B=31300, PWM_INICIAL=.25, PWM_FINAL=.60,
            FRENO_MS=50, HALL_LOOP_MS=1, pwm=PWM(), standby=Pin(5),
            monitor=Pin(18), in1=Pin(2), in2=Pin(3), opto=Pin(15))
        def stop():
            hw.standby.off(); hw.pwm.duty_u16(0); hw.in1.off(); hw.in2.off()
        def brake():
            stop(); hw.in1.on(); hw.in2.on(); hw.standby.on()
            return clock[0]
        hw.parar, hw.iniciar_freno = stop, brake
        hw.extremo_hall = lambda h: 'A' if h >= 40000 else 'B' if h <= 26000 else None
        machine = types.SimpleNamespace(Pin=Pin, ADC=ADC, WDT=WDT, WDT_RESET=3,
            reset_cause=lambda: 3 if mode == 'watchdog' else 0)
        time = types.SimpleNamespace(ticks_ms=lambda: clock[0], ticks_diff=lambda a,b:a-b, sleep_ms=sleep)
        with tempfile.TemporaryDirectory() as folder:
            spec = importlib.util.spec_from_file_location('vehicle_test', 'prueba_camioneta.py')
            module = importlib.util.module_from_spec(spec)
            with patch.dict('sys.modules', machine=machine, time=time, prueba_tb6612=hw), patch('builtins.print'):
                spec.loader.exec_module(module)
                module.DIRECTORIO = folder
                module.ARRANQUE_MS = 0
                module.DURACION_MS = duration
                # Registro accepts a directory name; use an existing relative temp subfolder.
                old = os.getcwd()
                os.chdir(folder)
                module.DIRECTORIO = 'logs'
                try:
                    original = module.Registro.flush
                    def checked_flush(log):
                        self.assertEqual(hw.standby.level, 0, 'Flash write while driver enabled')
                        if mode == 'disk_error': raise OSError('DISCO')
                        original(log)
                    with patch.object(module.Registro, 'flush', checked_flush):
                        with self.assertRaises(KeyboardInterrupt): module.ejecutar()
                    rows = []
                    for name in sorted(os.listdir('logs')):
                        with open('logs/' + name) as f:
                            rows += [json.loads(line) for line in f if line.strip()]
                finally:
                    os.chdir(old)
        self.assertEqual(hw.standby.level, 0)
        self.assertEqual(hw.monitor.level, 0)
        return rows, events

    def test_both_directions_brake_and_safe_flush(self):
        rows, events = self.simulate()
        self.assertEqual(rows[0]['rampa_ms'], 20)
        states = [r for r in rows if r['evento'] == 'ESTADO']
        moving = [r for r in states if r['direccion']]
        self.assertEqual(moving[0]['pwm'], .25)
        self.assertEqual(moving[1]['pwm'], .60)
        self.assertEqual({r['direccion'] for r in states}, {-1, 0, 1})
        self.assertTrue(any(r['frenando'] for r in states))
        self.assertEqual({r['posicion'] for r in states if r['estado']=='DETENIDO'}, {'A','B'})
        self.assertEqual(rows[-1]['motivo'], 'FIN_TIEMPO')

    def test_rapid_commands_do_not_starve_logging(self):
        rows, events = self.simulate('rapid')
        self.assertEqual(rows[-1]['motivo'], 'FIN_TIEMPO')
        self.assertGreater(len(rows), 256)
        self.assertGreater(sum(r.get('estado') == 'DETENIDO' for r in rows), 10)
        self.assertFalse(any(r.get('fallo') for r in rows))

    def test_saturation_stops_and_records(self):
        rows, _ = self.simulate('hall_error')
        self.assertIn('65535', rows[-1]['motivo'])

    def test_timeout_latches(self):
        rows, events = self.simulate('timeout')
        self.assertEqual(rows[-1]['motivo'], 'TIMEOUT')
        self.assertEqual(rows[0]['timeout_ms'], 3000)
        start = next(r['ms'] for r in rows if r.get('direccion'))
        self.assertGreaterEqual(rows[-1]['ms'] - start, 3000)
        self.assertLess(rows[-1]['ms'] - start, 3020)
        cutoff = rows[-1]['ms']
        self.assertFalse(any(t >= cutoff and n == 5 and v for t,n,v in events))

    def test_watchdog_reset_does_not_move(self):
        rows, events = self.simulate('watchdog')
        self.assertIn('RESET_WATCHDOG', rows[-1]['motivo'])
        self.assertFalse(any(n==5 and v for _,n,v in events))

    def test_storage_error_prevents_motion(self):
        rows, events = self.simulate('disk_error')
        self.assertFalse(any(n==5 and v for _,n,v in events))


if __name__ == '__main__':
    unittest.main()
