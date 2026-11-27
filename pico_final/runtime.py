"""Ejecucion permanente sin archivos; recuperacion y freno no bloqueantes."""
from .controller import Controller, configuration_errors


def validate(c):
    try:
        errors = configuration_errors(c)
        for name in ('STARTUP_MS', 'SETTLE_MS', 'HALL_STABLE_MS',
                     'COMMAND_STABLE_MS', 'REVERSE_PAUSE_MS', 'RAMP_MS',
                     'BRAKE_MS', 'LOOP_MS', 'RECOVERY_WAIT_MS',
                     'RECOVERY_VALID_MS', 'FAULT_BLINK_MS', 'CONSOLE_PENDING'):
            value = getattr(c, name)
            if type(value) is not int or value <= 0:
                errors.append(name)
        if not 1 <= c.HALL_SAMPLES <= 32 or type(c.HALL_SAMPLES) is not int:
            errors.append('HALL_SAMPLES')
        if type(c.WATCHDOG_MS) is not int or not 100 <= c.WATCHDOG_MS <= 8388:
            errors.append('WATCHDOG_MS')
        if type(c.PWM_HZ) is not int or not 1000 <= c.PWM_HZ <= 100000:
            errors.append('PWM_HZ')
        if c.VM_MONITOR_ENABLED:
            errors.append('VM_NO_INSTALADO')
        # El apagado de emergencia del lanzador corresponde a este montaje.
        pins = (c.PIN_STBY, c.PIN_MONITOR, c.PIN_IN1, c.PIN_IN2, c.PIN_PWM,
                c.PIN_COMMAND, c.PIN_HALL, c.PIN_GREEN, c.PIN_RED)
        if pins != (5, 18, 2, 3, 4, 15, 26, 16, 17):
            errors.append('PINOUT_MONTAJE')
        return errors
    except (AttributeError, TypeError, ValueError) as error:
        return ['CONFIG_INCOMPLETA: ' + str(error)]


class Clock:
    """Extiende ticks_ms usando ticks_diff, incluso al cruzar su desbordamiento."""
    def __init__(self, tick, diff):
        self.previous, self.diff, self.now = tick, diff, 0

    def update(self, tick):
        self.now += self.diff(tick, self.previous)
        self.previous = tick
        return self.now


class Engine:
    def __init__(self, c, hw, watchdog_reset=False):
        self.c, self.hw = c, hw
        self.active = 0
        self.brake_since = None
        self.brake_command = None
        self.monitor_on = False
        self.signal = None
        self.last_signal = None
        self.last_state = None
        self.pending = []
        self.fault = None
        self.fault_since = None
        self.valid_since = None
        self.valid_command = None
        self.hw.stop()
        self.errors = validate(c)
        self.control = None if self.errors else Controller(c)
        self.event('INICIO ' + c.VERSION)
        if self.errors:
            self.trip('CONFIG: ' + ', '.join(self.errors), 0)
        elif watchdog_reset:
            self.trip('RESET_WATCHDOG', 0)

    def event(self, message):
        # Diagnostico de consola acotado: no escribir flash ni bloquear el motor.
        limit = self.c.CONSOLE_PENDING if not self.errors else 16
        if len(self.pending) >= limit:
            self.pending.pop(0)
        self.pending.append(message)

    def trip(self, reason, now):
        self.hw.stop()
        self.active, self.brake_since = 0, None
        self.monitor_on = False
        self.fault, self.fault_since = reason, now
        self.valid_since, self.valid_command = None, None
        if self.control:
            self.control.was_moving = False
        self.event('FALLO ' + reason + ' | motor y Monitor apagados')

    def _recover(self, now, command, valid):
        self.hw.stop()
        if self.errors or now - self.fault_since < self.c.RECOVERY_WAIT_MS:
            return
        if not valid or command not in (0, 1):
            self.valid_since, self.valid_command = None, None
            return
        if command != self.valid_command or self.valid_since is None:
            self.valid_command, self.valid_since = command, now
        elif now - self.valid_since >= self.c.RECOVERY_VALID_MS:
            self.control = Controller(self.c)
            self.fault, self.fault_since = None, None
            self.last_state = None
            self.event('RECUPERACION | orden actual ' + ('CERRAR' if command == 0 else 'ABRIR'))

    def tick(self, now, command, hall, low, high):
        c = self.c
        valid = c.HALL_MIN < low <= hall <= high < c.HALL_MAX
        if self.fault:
            self._recover(now, command, valid)
            self.hw.indicators(None, True, now, c.FAULT_BLINK_MS)
            return
        if not valid:
            self.trip('HALL_INVALIDO min=%s max=%s' % (low, high), now)
            self.hw.indicators(None, True, now, c.FAULT_BLINK_MS)
            return
        out = self.control.step(now, command, hall, None)
        self.signal = out['signal']
        if self.signal is not None and self.signal != self.last_signal:
            self.event('ORDEN ' + ('CERRAR' if self.signal == 0 else 'ABRIR'))
            self.last_signal = self.signal
        if out['fault']:
            self.trip(out['fault'], now)
            self.hw.indicators(None, True, now, c.FAULT_BLINK_MS)
            return
        direction = out['direction']
        if not out['monitor']:
            self.hw.monitor.off()  # Antes de habilitar motor o freno.
        if self.brake_since is not None:
            if command != self.brake_command or now - self.brake_since >= c.BRAKE_MS:
                self.hw.stop()
                self.brake_since = None
            direction = 0
        elif not direction:
            reached = (hall >= c.HALL_A_ENTER if self.control.target == 'A'
                       else hall <= c.HALL_B_ENTER)
            if self.active and self.signal is not None and reached:
                self.hw.brake()
                self.brake_since, self.brake_command = now, command
            else:
                self.hw.stop()
        else:
            if direction != self.active:
                self.hw.stop()
            self.hw.drive(direction, out['duty'])
        self.active = direction
        # Contabilizar solo la marcha efectivamente aplicada, no el freno.
        self.control.was_moving = bool(direction)
        monitor = bool(out['monitor'] and not direction and self.brake_since is None)
        self.hw.monitor.value(monitor)
        if monitor != self.monitor_on:
            self.event('MONITOR ' + ('BAJO / ABIERTO' if monitor else 'ALTO'))
        self.monitor_on = monitor
        if out['state'] == 'DETENIDO' and self.last_state != 'DETENIDO':
            self.event('LLEGADA ' + self.control.target + ' Hall=' + str(hall))
        self.last_state = out['state']
        self.hw.indicators(self.signal, False, now, c.FAULT_BLINK_MS)

    def flush_console(self, emit):
        # Una linea por ciclo y SOLO con el puente apagado, tampoco durante freno.
        if not self.active and self.brake_since is None and self.pending:
            emit(self.pending.pop(0))


def run(c=None, machine_module=None, time_module=None, hardware_factory=None,
        emit=print):
    if c is None:
        from . import config as c
    if machine_module is None:
        import machine as machine_module
    if time_module is None:
        import time as time_module
    # Apagar antes de validar config o inicializar el resto del hardware.
    pin = machine_module.Pin
    pin(18, pin.OUT, value=0)
    pin(5, pin.OUT, value=0)
    pin('LED', pin.OUT, value=0)
    errors = validate(c)
    if errors:
        emit('CONFIG BLOQUEADA: ' + ', '.join(errors))
        red = pin(17, pin.OUT, value=0)
        watchdog = machine_module.WDT(timeout=1000)
        while True:
            pin(18, pin.OUT, value=0)
            pin(5, pin.OUT, value=0)
            red.value((time_module.ticks_ms() // 250) % 2)
            watchdog.feed()
            time_module.sleep_ms(50)
    if hardware_factory is None:
        from .hardware import Hardware as hardware_factory
    hw = hardware_factory(c)
    watchdog = machine_module.WDT(timeout=c.WATCHDOG_MS)
    clock = Clock(time_module.ticks_ms(), time_module.ticks_diff)
    engine = Engine(c, hw, machine_module.reset_cause() == machine_module.WDT_RESET)
    cancelled = False
    try:
        while True:
            try:
                now = clock.update(time_module.ticks_ms())
                if cancelled:
                    hw.stop()
                    hw.indicators(None, True, now, c.FAULT_BLINK_MS)
                else:
                    try:
                        engine.tick(now, *hw.read(c.HALL_SAMPLES))
                        watchdog.feed()
                        engine.flush_console(emit)
                    except Exception as error:
                        engine.trip('EXCEPCION ' + str(error)[:160], now)
                watchdog.feed()
                time_module.sleep_ms(c.LOOP_MS)
            except KeyboardInterrupt:
                hw.stop()
                if cancelled:
                    raise  # Segundo Ctrl+C permite acceso REPL; WDT sigue activo.
                cancelled = True  # Primero cancela incluso durante sleep_ms.
                engine.pending = []
                emit('CANCELADO | salidas apagadas; reiniciar para volver a controlar')
    finally:
        hw.stop()
