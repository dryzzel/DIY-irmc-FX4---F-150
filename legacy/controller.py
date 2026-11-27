"""Maquina de estados sin dependencias de hardware; tiempo monotono en ms."""


class Stable:
    def __init__(self, delay):
        self.delay = delay
        self.candidate = None
        self.since = 0

    def update(self, value, now):
        if value != self.candidate:
            self.candidate, self.since = value, now
        return value if now - self.since >= self.delay else None


def configuration_errors(c):
    errors = []
    if c.OPEN_END not in ('A', 'B'):
        errors.append('OPEN_END')
    if c.A_DIRECTION not in (-1, 1):
        errors.append('A_DIRECTION')
    if not isinstance(c.MOTION_TIMEOUT_MS, int) or not 50 <= c.MOTION_TIMEOUT_MS <= 10000:
        errors.append('MOTION_TIMEOUT_MS')
    if not (c.HALL_MIN < c.HALL_B_ENTER < c.HALL_B_EXIT < c.HALL_A_EXIT < c.HALL_A_ENTER < c.HALL_MAX):
        errors.append('HALL_THRESHOLDS')
    if not 0 < c.PWM_START <= c.PWM_RUN <= 1:
        errors.append('PWM')
    return errors


class Controller:
    def __init__(self, cfg):
        self.c = cfg
        self.errors = configuration_errors(cfg)
        self.state = 'INICIO'
        self.fault = None
        self.target = None
        self.position = 'MID'
        self.hall_filter = Stable(cfg.HALL_STABLE_MS)
        self.command_filter = Stable(cfg.COMMAND_STABLE_MS)
        self.ready_since = None
        self.wait_since = 0
        self.move_since = 0
        self.motion_budget = 0
        self.last_now = 0
        self.was_moving = False
        self.settle_since = 0

    def fail(self, reason):
        self.fault = reason
        self.state = 'FALLO'

    def _hall(self, value):
        c = self.c
        if self.position == 'A' and value > c.HALL_A_EXIT:
            return 'A'
        if self.position == 'B' and value < c.HALL_B_EXIT:
            return 'B'
        if value > c.HALL_A_ENTER:
            return 'A'
        if value < c.HALL_B_ENTER:
            return 'B'
        return 'MID'

    def step(self, now, command, hall, vm):
        c = self.c
        dt = max(0, now - self.last_now)
        self.last_now = now
        if self.was_moving:
            self.motion_budget += dt
        self.was_moving = False
        signal = self.command_filter.update(command, now)
        hall_valid = c.HALL_MIN < hall < c.HALL_MAX
        self.position = self._hall(hall) if hall_valid else 'INVALID'
        position = self.hall_filter.update(self.position, now)
        out = {'state': self.state, 'direction': 0, 'duty': 0.0,
               'monitor': False, 'signal': signal, 'position': position, 'fault': self.fault}
        if not c.DRIVE_ENABLED:
            self.state = 'DIAGNOSTICO'
        elif self.errors:
            self.fail('CONFIG: ' + ', '.join(self.errors))
        elif not self.fault:
            if not hall_valid:
                self.fail('HALL_INVALIDO')
            elif getattr(c, 'VM_MONITOR_ENABLED', True) and (vm is None or not c.VM_MIN <= vm <= c.VM_MAX):
                if self.ready_since is not None and self.state != 'INICIO':
                    self.fail('ALIMENTACION')
                self.ready_since = None
            else:
                if self.ready_since is None:
                    self.ready_since = now
                if now - self.ready_since >= c.STARTUP_MS and signal is not None and position is not None:
                    destination = c.OPEN_END if signal == 1 else ('B' if c.OPEN_END == 'A' else 'A')
                    if destination != self.target:
                        self.target = destination
                        self.wait_since = now
                        self.state = 'PAUSA'
                    if position == destination:
                        if self.state not in ('ASENTANDO', 'DETENIDO') or self.settle_since is None:
                            self.settle_since = now
                            self.state = 'ASENTANDO'
                        if now - self.settle_since >= c.SETTLE_MS:
                            self.state = 'DETENIDO'
                            self.motion_budget = 0
                        out['monitor'] = bool(c.MONITOR_ENABLED and self.state == 'DETENIDO'
                                              and position == c.OPEN_END and signal == 1)
                    elif self.state in ('ASENTANDO', 'DETENIDO'):
                        self.fail('POSICION_PERDIDA')
                    elif self.motion_budget >= c.MOTION_TIMEOUT_MS:
                        self.fail('TIMEOUT')
                    elif now - self.wait_since >= c.REVERSE_PAUSE_MS:
                        if self.state != 'MOVIENDO':
                            self.move_since = now
                        self.state = 'MOVIENDO'
                        ramp = min(1.0, (now - self.move_since) / max(1, c.RAMP_MS))
                        out['direction'] = c.A_DIRECTION if destination == 'A' else -c.A_DIRECTION
                        out['duty'] = c.PWM_START + (c.PWM_RUN - c.PWM_START) * ramp
                        self.was_moving = True
                elif self.state == 'MOVIENDO':
                    self.state = 'PAUSA'
                    self.wait_since = now
                elif self.state in ('ASENTANDO', 'DETENIDO'):
                    # Ruido de comando/Hall invalida el asentamiento anterior.
                    # Reiniciar el intervalo cuando AMBAS lecturas sean estables.
                    self.state = 'ASENTANDO'
                    self.settle_since = None
        if self.fault:
            out['direction'], out['duty'], out['monitor'] = 0, 0.0, False
            self.was_moving = False
        out['state'], out['fault'] = self.state, self.fault
        return out
