"""CMCV Pico + TB6612 paralelo. Revisar config.py antes de habilitar movimiento."""
from machine import Pin, PWM, ADC, WDT
from time import ticks_ms, ticks_diff, sleep_ms

# Deshabilitar potencia antes de importar configuracion/controlador.
standby = Pin(5, Pin.OUT, value=0)
monitor = Pin(18, Pin.OUT, value=0)
in1 = Pin(2, Pin.OUT, value=0)
in2 = Pin(3, Pin.OUT, value=0)
pwm = PWM(Pin(4))
pwm.duty_u16(0)
green = Pin(16, Pin.OUT, value=0)
red = Pin(17, Pin.OUT, value=0)


def stop():
    standby.off()  # Alta impedancia: rueda libre, NO freno activo.
    pwm.duty_u16(0)
    in1.off()
    in2.off()


def run():
    import config as cfg
    from controller import Controller
    control = Controller(cfg)
    pwm.freq(cfg.PWM_HZ)
    opto = Pin(15, Pin.IN, Pin.PULL_UP)
    hall, voltage = ADC(26), ADC(28)
    import machine
    if machine.reset_cause() == machine.WDT_RESET:
        control.fail('RESET_WATCHDOG')
    watchdog = WDT(timeout=500)
    print('CMCV: modo', 'CONTROL' if cfg.DRIVE_ENABLED else 'DIAGNOSTICO')
    print('Pendientes de configuracion:', control.errors)
    previous_tick = ticks_ms()
    now = 0
    last_report = -1000
    previous_state = None
    active_direction = 0
    while True:
        tick = ticks_ms()
        now += ticks_diff(tick, previous_tick)
        previous_tick = tick
        h = sum(hall.read_u16() for _ in range(8)) // 8
        vm = voltage.read_u16() * cfg.ADC_REFERENCE / 65535 * cfg.VM_DIVIDER
        out = control.step(now, opto.value(), h, vm)
        direction = out['direction']
        if direction == 0:
            stop()
        else:
            if direction != active_direction:
                stop()
                in1.value(direction == 1)
                in2.value(direction == -1)
            pwm.duty_u16(int(out['duty'] * 65535))
            standby.on()
        active_direction = direction
        monitor.value(out['monitor'])
        if out['fault']:
            green.off()
            red.value((now // 250) % 2)
        else:
            green.value(out['signal'] == 0)
            red.value(out['signal'] == 1)
        if out['state'] != previous_state or now - last_report >= 1000:
            print('estado={} Hall={} extremo={} VM={:.2f} Monitor={} fallo={}'.format(
                out['state'], h, out['position'], vm, out['monitor'], out['fault']))
            previous_state, last_report = out['state'], now
        watchdog.feed()
        sleep_ms(cfg.LOOP_MS)


try:
    run()
finally:
    stop()
    monitor.off()
    green.off()
    red.off()
    pwm.deinit()
