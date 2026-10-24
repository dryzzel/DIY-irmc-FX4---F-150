"""Automatico temporal con registro. Ver PRUEBA_CAMIONETA.md antes de instalar."""
import os
import json
import machine
from time import ticks_ms, ticks_diff, sleep_ms
import prueba_tb6612 as hw  # Inicializa salidas apagadas; NO ejecuta el menu.
from controller import Controller
import config as base

DURACION_MS = 10 * 60 * 1000
ARRANQUE_MS = 5000
DIRECTORIO = 'logs_cmcv'
MAX_ARCHIVOS = 8
MAX_BYTES = 128 * 1024
MAX_PENDIENTES = 256


def configuracion():
    class Prueba:
        pass
    c = Prueba()
    for name in dir(base):
        if name.isupper():
            setattr(c, name, getattr(base, name))
    c.DRIVE_ENABLED = True
    c.MONITOR_ENABLED = False
    c.VM_MONITOR_ENABLED = False
    c.OPEN_END = 'B'
    c.A_DIRECTION = hw.DIRECCION_A
    c.MOTION_TIMEOUT_MS = 2000
    c.HALL_A_ENTER, c.HALL_A_EXIT = hw.TOPE_A, hw.RETENCION_A
    c.HALL_B_ENTER, c.HALL_B_EXIT = hw.TOPE_B, hw.RETENCION_B
    c.PWM_START, c.PWM_RUN = hw.PWM_INICIAL, hw.PWM_FINAL
    return c


class Registro:
    def __init__(self):
        if DIRECTORIO not in os.listdir():
            os.mkdir(DIRECTORIO)
        names = os.listdir(DIRECTORIO)
        self.path = None
        for n in range(1, MAX_ARCHIVOS + 1):
            name = 'prueba_%02d.jsonl' % n
            if name not in names:
                self.path = DIRECTORIO + '/' + name
                break
        if self.path is None:
            raise OSError('REGISTROS_LLENO: descargar y borrar registros anteriores')
        self.pending = []
        self.size = 0
        with open(self.path, 'w') as f:
            f.write('')

    def add(self, event):
        if len(self.pending) >= MAX_PENDIENTES:
            raise OSError('BUFFER_LLENO')
        self.pending.append(event)

    def flush(self):
        # Llamar SOLO con STBY=0, sin movimiento ni freno.
        with open(self.path, 'a') as f:
            while self.pending:
                line = json.dumps(self.pending[0]) + '\n'
                if self.size + len(line) > MAX_BYTES:
                    raise OSError('REGISTRO_LLENO')
                f.write(line)
                self.size += len(line)
                self.pending.pop(0)
            f.flush()
        if hasattr(os, 'sync'):
            os.sync()


def ejecutar():
    hw.parar()
    hw.monitor.off()
    green = machine.Pin(16, machine.Pin.OUT, value=0)
    red = machine.Pin(17, machine.Pin.OUT, value=0)
    log = None
    watchdog = None
    now = 0
    reason = None
    try:
        c = configuracion()
        control = Controller(c)
        log = Registro()
        reset = machine.reset_cause()
        log.add({'evento': 'INICIO', 'version': 1, 'ms': 0, 'reset': reset,
                 'direccion_A': c.A_DIRECTION, 'open_end': c.OPEN_END,
                 'pwm': c.PWM_RUN, 'freno_ms': hw.FRENO_MS,
                 'umbral_A': c.HALL_A_ENTER, 'umbral_B': c.HALL_B_ENTER,
                 'retencion_A': c.HALL_A_EXIT, 'retencion_B': c.HALL_B_EXIT,
                 'timeout_ms': c.MOTION_TIMEOUT_MS, 'monitor': False,
                 'supervision_vm': False, 'duracion_ms': DURACION_MS})
        log.flush()
        if reset == machine.WDT_RESET:
            raise ValueError('RESET_WATCHDOG: movimiento bloqueado')
        if control.errors:
            raise ValueError('CONFIG: ' + ', '.join(control.errors))
        watchdog = machine.WDT(timeout=1000)
        hw.pwm.freq(c.PWM_HZ)
        sensor = machine.ADC(26)
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < ARRANQUE_MS:
            green.value((ticks_diff(ticks_ms(), start) // 250) % 2)
            red.value(green.value())
            watchdog.feed()
            sleep_ms(20)
        previous = ticks_ms()
        last_read = previous
        active = 0
        brake = None
        brake_command = None
        last_state = None
        last_sample = -5000
        last_flush = 0
        last_power = 0
        max_interval = 0
        raw_min, raw_max = 65535, 0
        while now < DURACION_MS:
            tick = ticks_ms()
            now += ticks_diff(tick, previous)
            previous = tick
            values = [sensor.read_u16() for _ in range(8)]
            low, high = min(values), max(values)
            hall = sum(values) // 8
            read_tick = ticks_ms()
            if active or brake is not None:
                max_interval = max(max_interval, ticks_diff(read_tick, last_read))
            last_read = read_tick
            raw_min, raw_max = min(raw_min, low), max(raw_max, high)
            if low <= c.HALL_MIN or high >= c.HALL_MAX:
                raise ValueError('HALL_RANGO min=%s max=%s media=%s' % (low, high, hall))
            command = hw.opto.value()
            out = control.step(now, command, hall, None)
            direction = out['direction']
            if brake is not None:
                if out['fault'] or command != brake_command or ticks_diff(ticks_ms(), brake) >= hw.FRENO_MS:
                    hw.parar()
                    brake = None
                direction = 0
            elif not direction:
                if active and not out['fault'] and out['signal'] is not None and hw.extremo_hall(hall) == control.target:
                    brake = hw.iniciar_freno()
                    brake_command = command
                else:
                    hw.parar()
            else:
                if direction != active:
                    hw.parar()
                    hw.in1.value(direction == 1)
                    hw.in2.value(direction == -1)
                hw.pwm.duty_u16(int(out['duty'] * 65535))
                hw.standby.on()
            active = direction
            if active or brake is not None:
                last_power = now
            green.value(out['signal'] == 0)
            red.value(out['signal'] == 1)
            state = (out['state'], command, out['signal'], control.target, active, brake is not None, out['fault'])
            recent = active or brake is not None or now - last_power < 800
            if state != last_state or now - last_sample >= (50 if recent else 5000):
                log.add({'evento': 'ESTADO', 'ms': now, 'gp15': command,
                         'senal': out['signal'], 'destino': control.target,
                         'estado': out['state'], 'posicion': out['position'],
                         'hall': hall, 'crudo_min': raw_min, 'crudo_max': raw_max,
                         'intervalo_hall_max_ms': max_interval,
                         'direccion': active, 'pwm': out['duty'] if active else 0,
                         'frenando': brake is not None, 'fallo': out['fault']})
                raw_min, raw_max, max_interval = 65535, 0, 0
                last_sample, last_state = now, state
            if out['fault']:
                raise ValueError(out['fault'])
            if (not active and brake is None and out['state'] == 'DETENIDO'
                    and now - last_power >= 800
                    and (recent or now - last_flush >= 1000)):
                hw.parar()
                watchdog.feed()
                log.flush()
                last_flush = now
            watchdog.feed()
            sleep_ms(hw.HALL_LOOP_MS)
        reason = 'FIN_TIEMPO'
    except KeyboardInterrupt:
        reason = 'CANCELADO'
    except Exception as error:
        reason = str(error)
    finally:
        hw.parar()
        hw.monitor.off()
        green.off()
        red.on()
        if log is not None:
            try:
                # Priorizar guardar el error aun si el buffer se lleno.
                if len(log.pending) >= MAX_PENDIENTES:
                    log.pending.pop()
                log.add({'evento': 'FIN', 'ms': now, 'motivo': reason})
                if watchdog:
                    watchdog.feed()
                log.flush()
            except Exception as error:
                print('Error guardando registro:', error)
        print('Prueba detenida:', reason, '| archivo:', log.path if log else None)
    # El WDT no se puede desactivar: esperar con potencia apagada.
    # Ctrl+C vuelve al editor; un reset posterior de WDT no habilita movimiento.
    while True:
        hw.parar()
        red.value((ticks_ms() // 250) % 2)
        if watchdog:
            watchdog.feed()
        sleep_ms(50)


if __name__ == '__main__':
    ejecutar()
