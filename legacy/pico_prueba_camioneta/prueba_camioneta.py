"""Automatico temporal con registro. Ver PRUEBA_CAMIONETA.md antes de instalar."""
import os
import json
import machine
from time import ticks_ms, ticks_diff, sleep_ms
import prueba_tb6612 as hw  # Inicializa salidas apagadas; NO ejecuta el menu.
from controller import Controller
import config as base

DURACION_MS = 2 * 60 * 60 * 1000  # Ventana de observacion: dos horas.
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
    c.MONITOR_ENABLED = True
    c.VM_MONITOR_ENABLED = False
    c.OPEN_END = 'B'
    c.A_DIRECTION = hw.DIRECCION_A
    c.MOTION_TIMEOUT_MS = 3000
    c.HALL_A_ENTER, c.HALL_A_EXIT = hw.TOPE_A, hw.RETENCION_A
    c.HALL_B_ENTER, c.HALL_B_EXIT = hw.TOPE_B, hw.RETENCION_B
    c.PWM_START, c.PWM_RUN = hw.PWM_INICIAL, hw.PWM_FINAL
    c.RAMP_MS = 20  # Rampa corta: 25% -> 70% en 20 ms.
    return c


class Registro:
    RESERVA_FIN = 1024

    def __init__(self):
        if DIRECTORIO not in os.listdir():
            os.mkdir(DIRECTORIO)
        self.pending = []
        self.size = 0
        self.heartbeat = None
        self.path = None
        self._nuevo()

    def _nuevo(self):
        names = os.listdir(DIRECTORIO)
        for n in range(1, MAX_ARCHIVOS + 1):
            name = 'prueba_%02d.jsonl' % n
            if name not in names:
                path = DIRECTORIO + '/' + name
                with open(path, 'w') as f:
                    f.write('')
                self.path, self.size = path, 0
                return
        raise OSError('REGISTROS_LLENO: descargar y borrar registros anteriores')

    def _latido(self):
        if self.heartbeat:
            self.heartbeat()

    def add(self, event):
        if len(self.pending) >= MAX_PENDIENTES:
            raise OSError('BUFFER_LLENO')
        self.pending.append(event)

    def flush(self):
        # Solo STBY=0. Escrituras por lotes, con latido entre lineas.
        if not self.pending:
            return
        f = None
        try:
            while self.pending:
                event = self.pending[0]
                line = json.dumps(event) + '\n'
                terminal = event.get('evento') == 'FIN'
                limit = MAX_BYTES if terminal else MAX_BYTES - self.RESERVA_FIN
                if len(line) > limit:
                    raise OSError('LINEA_REGISTRO_DEMASIADO_GRANDE')
                if self.size + len(line) > limit:
                    if f is not None:
                        f.flush()
                        f.close()
                        f = None
                    self._latido()
                    previous = self.path
                    self._nuevo()
                    self.pending.insert(0, {'evento': 'CONTINUACION',
                                           'anterior': previous, 'ms': event.get('ms')})
                    continue
                if f is None:
                    f = open(self.path, 'a')
                f.write(line)
                self.size += len(line)
                self.pending.pop(0)
                self._latido()
            f.flush()
            self._latido()
        finally:
            if f is not None:
                f.close()
        if hasattr(os, 'sync'):
            os.sync()
        self._latido()

    def finish(self, event):
        # Un error de capacidad no debe impedir registrar por que se detuvo.
        try:
            self.flush()
        except OSError as error:
            event['error_registro'] = str(error)[:200]
            event['pendientes_descartados'] = len(self.pending)
            self.pending = []
        self.add(event)
        self.flush()


def ejecutar():
    import indicador_imrc
    hw.parar()
    hw.monitor.off()
    green = machine.Pin(16, machine.Pin.OUT, value=0)
    red = machine.Pin(17, machine.Pin.OUT, value=0)
    log = None
    watchdog = None
    now = 0
    reason = None
    try:
        indicador_imrc.iniciar(hw.opto)
        c = configuracion()
        control = Controller(c)
        log = Registro()
        reset = machine.reset_cause()
        log.add({'evento': 'INICIO', 'version': 6, 'registro': 'eventos', 'resumen_ms': 60000, 'ms': 0, 'reset': reset,
                 'direccion_A': c.A_DIRECTION, 'open_end': c.OPEN_END,
                 'pwm': c.PWM_RUN, 'pwm_inicial': c.PWM_START,
                 'rampa_ms': c.RAMP_MS, 'freno_ms': hw.FRENO_MS,
                 'umbral_A': c.HALL_A_ENTER, 'umbral_B': c.HALL_B_ENTER,
                 'retencion_A': c.HALL_A_EXIT, 'retencion_B': c.HALL_B_EXIT,
                 'timeout_ms': c.MOTION_TIMEOUT_MS, 'monitor': c.MONITOR_ENABLED,
                 'supervision_vm': False, 'duracion_ms': DURACION_MS})
        log.flush()
        if reset == machine.WDT_RESET:
            raise ValueError('RESET_WATCHDOG: movimiento bloqueado')
        if control.errors:
            raise ValueError('CONFIG: ' + ', '.join(control.errors))
        watchdog = machine.WDT(timeout=1000)
        def latido_registro():
            if hw.standby.value():
                raise ValueError('ESCRITURA_CON_DRIVER_ACTIVO')
            watchdog.feed()
        log.heartbeat = latido_registro
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
        last_sample = 0
        last_signal = None
        cambios_orden = 0
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
            if not out['monitor']:
                hw.monitor.off()  # Liberar antes de cualquier nuevo movimiento.
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
            monitor_on = bool(out['monitor'] and not active and brake is None)
            hw.monitor.value(monitor_on)
            if active or brake is not None:
                last_power = now
            green.value(out['signal'] == 0)
            red.value(out['signal'] == 1)
            # Registrar solo ordenes estables; None durante el filtro no es otra orden.
            if out['signal'] is not None and out['signal'] != last_signal:
                inicial = last_signal is None
                if not inicial:
                    cambios_orden += 1
                log.add({'evento': 'SENAL_INICIAL' if inicial else 'ORDEN_PCM',
                         'ms': now, 'gp15': out['signal'],
                         'orden': 'CERRAR' if out['signal'] == 0 else 'ABRIR',
                         'anterior': last_signal, 'cambios_orden': cambios_orden,
                         'hall': hall})
                last_signal = out['signal']
            state = (out['state'], control.target, active, brake is not None, out['fault'], monitor_on)
            cambio = state != last_state
            if cambio or now - last_sample >= 60000:
                log.add({'evento': 'ESTADO' if cambio else 'RESUMEN', 'ms': now, 'gp15': command,
                         'senal': out['signal'], 'destino': control.target,
                         'estado': out['state'], 'posicion': out['position'],
                         'hall': hall, 'crudo_min': raw_min, 'crudo_max': raw_max,
                         'intervalo_hall_max_ms': max_interval,
                         'direccion': active, 'pwm': out['duty'] if active else 0,
                         'frenando': brake is not None, 'fallo': out['fault'],
                         'monitor_gp18': int(monitor_on),
                         'monitor_nivel_esperado': 'BAJO' if monitor_on else 'ALTO'})
                raw_min, raw_max, max_interval = 65535, 0, 0
                last_sample, last_state = now, state
            if out['fault']:
                raise ValueError(out['fault'])
            # Vaciar preventivamente durante pausas: las ordenes frecuentes
            # pueden impedir que exista una ventana de 800 ms en DETENIDO.
            urgente = len(log.pending) >= 64
            reposo = (out['state'] == 'DETENIDO' and now - last_power >= 800
                      and now - last_flush >= 1000)
            if (not active and brake is None and now - last_power >= 50
                    and out['state'] in ('INICIO', 'PAUSA', 'ASENTANDO', 'DETENIDO')
                    and (urgente or reposo)):
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
                if watchdog:
                    watchdog.feed()
                log.finish({'evento': 'FIN', 'ms': now, 'motivo': reason,
                            'monitor_gp18': 0, 'monitor_nivel_esperado': 'ALTO'})
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
