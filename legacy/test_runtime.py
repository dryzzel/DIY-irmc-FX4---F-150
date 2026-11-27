"""Ejecuta main.py con periféricos simulados; no certifica MicroPython/hardware."""
import runpy
import types
import unittest
from unittest.mock import patch
import config


class RuntimeTests(unittest.TestCase):
    def execute(self, drive=False, watchdog_reset=False, adc_failure=False):
        clock = [0]
        pins = {}
        events = []
        pwm_objects = []
        adc_channels = []

        class Pin:
            IN, OUT, PULL_UP = 0, 1, 2

            def __init__(self, number, mode=None, value=None):
                self.number = number
                self.level = 1 if number == 15 else (value or 0)
                pins[number] = self

            def value(self, level=None):
                if level is not None:
                    self.level = int(level)
                    events.append((clock[0], self.number, self.level))
                return self.level

            def on(self): self.value(1)
            def off(self): self.value(0)

        class PWM:
            def __init__(self, pin):
                self.duty = 0
                self.closed = False
                pwm_objects.append(self)

            def freq(self, value): self.frequency = value
            def duty_u16(self, value): self.duty = value
            def deinit(self): self.closed = True

        class ADC:
            def __init__(self, number):
                self.number = number
                adc_channels.append(number)

            def read_u16(self):
                if adc_failure and clock[0] >= 1000:
                    raise OSError('ADC simulado')
                if self.number == 26:
                    return 32000 if clock[0] < 1000 else 38600
                return int(12 / config.VM_DIVIDER / 3.3 * 65535)

        class WDT:
            def __init__(self, timeout): self.timeout = timeout
            def feed(self): pass

        def sleep_ms(ms):
            clock[0] += ms
            if clock[0] >= 1500:
                raise KeyboardInterrupt

        machine = types.SimpleNamespace(Pin=Pin, PWM=PWM, ADC=ADC, WDT=WDT,
                                        reset_cause=lambda: 3 if watchdog_reset else 0, WDT_RESET=3)
        fake_time = types.SimpleNamespace(ticks_ms=lambda: clock[0], ticks_diff=lambda a, b: a-b,
                                          sleep_ms=sleep_ms)
        values = dict(DRIVE_ENABLED=drive, MONITOR_ENABLED=True, OPEN_END='A', A_DIRECTION=1,
                      MOTION_TIMEOUT_MS=1000)
        with patch.dict('sys.modules', machine=machine, time=fake_time), patch.multiple(config, **values), patch('builtins.print'):
            with self.assertRaises(OSError if adc_failure else KeyboardInterrupt):
                runpy.run_path('main.py', run_name='__main__')
        for number in (5, 18, 2, 3, 16, 17):
            self.assertEqual(pins[number].level, 0)
        self.assertEqual(adc_channels, [26, 28])
        self.assertTrue(pwm_objects[0].closed)
        return events

    def test_diagnostic_never_enables_motor_or_monitor(self):
        events = self.execute()
        self.assertFalse(any(pin in (5, 18) and level for _, pin, level in events))

    def test_motion_then_monitor_and_cleanup(self):
        events = self.execute(drive=True)
        self.assertTrue(any(pin == 5 and level for _, pin, level in events))
        self.assertTrue(any(pin == 18 and level for _, pin, level in events))
        self.assertFalse(any(t < 1180 and pin == 18 and level for t, pin, level in events))

    def test_watchdog_reset_stays_disabled(self):
        events = self.execute(drive=True, watchdog_reset=True)
        self.assertFalse(any(pin in (5, 18) and level for _, pin, level in events))

    def test_adc_exception_cleans_up_outputs(self):
        self.execute(drive=True, adc_failure=True)


if __name__ == '__main__':
    unittest.main()
