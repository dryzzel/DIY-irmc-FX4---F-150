"""TB6612, Hall y Monitor. Sin menus, archivos ni LED integrado de actividad."""
from machine import Pin, PWM, ADC


class Hardware:
    def __init__(self, c):
        self.standby = Pin(c.PIN_STBY, Pin.OUT, value=0)
        self.monitor = Pin(c.PIN_MONITOR, Pin.OUT, value=0)
        self.led = Pin('LED', Pin.OUT, value=0)
        self.in1 = Pin(c.PIN_IN1, Pin.OUT, value=0)
        self.in2 = Pin(c.PIN_IN2, Pin.OUT, value=0)
        self.pwm = PWM(Pin(c.PIN_PWM))
        self.pwm.duty_u16(0)
        self.pwm.freq(c.PWM_HZ)
        self.command = Pin(c.PIN_COMMAND, Pin.IN, Pin.PULL_UP)
        self.command.irq(handler=None)  # Retirar tambien un IRQ de pruebas previas.
        self.sensor = ADC(c.PIN_HALL)
        self.green = Pin(c.PIN_GREEN, Pin.OUT, value=0)
        self.red = Pin(c.PIN_RED, Pin.OUT, value=0)

    def stop(self):
        self.monitor.off()
        self.standby.off()
        self.pwm.duty_u16(0)
        self.in1.off()
        self.in2.off()

    def drive(self, direction, duty):
        self.monitor.off()
        self.in1.value(direction == 1)
        self.in2.value(direction == -1)
        self.pwm.duty_u16(int(duty * 65535))
        self.standby.on()

    def brake(self):
        self.stop()
        self.in1.on()
        self.in2.on()
        self.standby.on()  # IN1=IN2=1, PWM=0: freno corto en ambos puentes.

    def read(self, count):
        total, low, high = 0, 65535, 0
        for _ in range(count):
            value = self.sensor.read_u16()
            total += value
            low, high = min(low, value), max(high, value)
        return self.command.value(), total // count, low, high

    def indicators(self, signal, fault, now, blink_ms):
        self.green.value(not fault and signal == 0)
        self.red.value((now // blink_ms) % 2 if fault else signal == 1)
