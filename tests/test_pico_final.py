import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pico_final import config
from pico_final.controller import Controller
from pico_final.runtime import Engine, Clock, run, validate


def settings(**changes):
    data = {k: v for k, v in vars(config).items() if k.isupper()}
    data.update(changes)
    return SimpleNamespace(**data)


class Output:
    def __init__(self, hw):
        self.hw = hw
        self.level = 0

    def value(self, v=None):
        if v is not None:
            assert not v or self.hw.mode == 'off', 'Monitor simultaneo con puente activo'
            self.level = int(v)
        return self.level

    def off(self):
        self.value(0)


class FakeHardware:
    def __init__(self, c=None):
        self.mode = 'off'
        self.monitor = Output(self)
        self.direction = 0
        self.duty = 0
        self.history = []
        self.sample = (1, 20000, 19990, 20010)
        self.leds = None

    def stop(self):
        self.monitor.off()
        self.mode, self.direction, self.duty = 'off', 0, 0

    def drive(self, direction, duty):
        assert not self.monitor.level
        assert not self.direction or self.direction == direction
        self.mode, self.direction, self.duty = 'drive', direction, duty
        self.history.append((direction, duty))

    def brake(self):
        assert not self.monitor.level
        self.mode, self.direction = 'brake', 0

    def read(self, count):
        return self.sample

    def indicators(self, *args):
        self.leds = args


class FinalTests(unittest.TestCase):
    def advance(self, engine, start, end, command=1, hall=32700, step=5):
        for now in range(start, end + 1, step):
            engine.tick(now, command, hall, hall - 5, hall + 5)

    def engine(self, **changes):
        hw = FakeHardware()
        return Engine(settings(**changes), hw), hw

    def test_effective_settings_and_early_start(self):
        e, hw = self.engine()
        self.advance(e, 0, 795)
        self.assertEqual(hw.mode, 'off')
        e.tick(800, 1, 32700, 32695, 32705)
        self.assertEqual(hw.duty, .40)
        self.advance(e, 805, 820)
        self.assertAlmostEqual(hw.duty, .70)
        self.assertEqual(config.MOTION_TIMEOUT_MS, 3000)
        self.assertEqual(validate(config), [])

    def test_new_stable_order_gets_full_budget(self):
        e, hw = self.engine()
        self.advance(e, 0, 2300)  # 1500 ms abriendo.
        self.assertEqual(e.control.motion_budget, 1500)
        self.advance(e, 2305, 2350, command=0)
        self.assertGreaterEqual(e.control.motion_budget, 1500)  # Aun no estable.
        e.tick(2355, 0, 32700, 32695, 32705)
        self.assertEqual(e.control.motion_budget, 0)
        self.advance(e, 2360, 2650, command=0)
        self.assertEqual(hw.mode, 'off')
        self.advance(e, 2655, 4450, command=0)  # Otros 1795 ms cerrando.
        self.assertIsNone(e.fault)
        self.assertEqual(hw.direction, 1)
        self.advance(e, 4455, 4700, command=0, hall=45000)
        self.assertEqual(e.control.state, 'DETENIDO')
        self.assertEqual(e.control.motion_budget, 0)

    def test_noise_and_pause_do_not_reset_budget(self):
        e, hw = self.engine()
        self.advance(e, 0, 1800)
        before = e.control.motion_budget
        e.tick(1805, 0, 32700, 32695, 32705)
        self.advance(e, 1810, 1900)
        self.assertGreaterEqual(e.control.motion_budget, before)
        self.assertEqual(hw.mode, 'off')
        self.advance(e, 1905, 4500)
        self.assertEqual(e.fault, 'TIMEOUT')
        self.assertEqual(hw.mode, 'off')

    def test_leaving_start_endpoint_does_not_reset_budget(self):
        e, hw = self.engine()
        self.advance(e, 0, 850, command=0, hall=20000)
        self.assertTrue(e.control.motion_budget > 0)
        prior = e.control.motion_budget
        e.tick(855, 0, 32700, 32695, 32705)
        self.advance(e, 860, 1150, command=0)
        self.assertGreaterEqual(e.control.motion_budget, prior)

    def test_brake_monitor_and_close_order(self):
        e, hw = self.engine()
        self.advance(e, 0, 1000)
        e.tick(1005, 1, 26000, 25995, 26005)
        self.assertEqual(hw.mode, 'brake')
        self.assertEqual(hw.monitor.level, 0)
        self.advance(e, 1010, 1050, hall=20000)
        self.assertEqual(hw.mode, 'brake')
        self.advance(e, 1055, 1250, hall=20000)
        self.assertEqual(hw.mode, 'off')
        self.assertEqual(hw.monitor.level, 1)
        e.tick(1255, 0, 20000, 19995, 20005)
        self.assertEqual(hw.monitor.level, 0)
        self.advance(e, 1260, 1660, command=0, hall=20000)
        self.assertEqual(hw.direction, 1)

    def test_brake_cancelled_by_command_change(self):
        e, hw = self.engine()
        self.advance(e, 0, 1000)
        e.tick(1005, 1, 25000, 24995, 25005)
        e.tick(1010, 0, 20000, 19995, 20005)
        self.assertIsNone(e.brake_since)
        self.assertEqual(hw.mode, 'off')

    def test_inclusive_thresholds(self):
        for command, hall, end in ((0, 40000, 'A'), (1, 26000, 'B')):
            e, hw = self.engine()
            self.advance(e, 0, 700, command=command, hall=hall)
            self.assertEqual(e.control.position, end)
            self.assertEqual(e.control.state, 'DETENIDO')
            self.assertEqual(hw.monitor.level, int(command == 1))

    def test_raw_spike_stops_even_when_average_valid(self):
        e, hw = self.engine()
        self.advance(e, 0, 850)
        e.tick(855, 1, 32700, 32600, 65535)
        self.assertIn('HALL_INVALIDO', e.fault)
        self.assertEqual(hw.mode, 'off')
        self.assertEqual(hw.monitor.level, 0)

    def test_position_loss_recovers_current_order(self):
        e, hw = self.engine()
        self.advance(e, 0, 800, hall=20000)
        self.advance(e, 805, 850)
        self.assertEqual(e.fault, 'POSICION_PERDIDA')
        since = e.fault_since
        self.advance(e, 855, since + 29995, command=0)
        self.assertEqual(hw.mode, 'off')
        self.advance(e, since + 30000, since + 31000, command=0)
        self.assertIsNone(e.fault)
        self.advance(e, since + 31005, since + 31810, command=0)
        self.assertEqual(e.control.target, 'A')
        self.assertEqual(hw.direction, 1)

    def test_recovery_requires_valid_hall_and_continuous_command(self):
        e, hw = self.engine()
        e.trip('TIMEOUT', 0)
        for now in range(0, 31001, 100):
            e.tick(now, 1, 32700, 0, 65535)
        self.assertIsNotNone(e.fault)
        for now in range(31100, 34001, 100):
            e.tick(now, (now // 100) % 2, 32700, 32695, 32705)
        self.assertIsNotNone(e.fault)
        self.advance(e, 34100, 35100, command=1)
        self.assertIsNone(e.fault)
        self.assertEqual(hw.mode, 'off')

    def test_watchdog_recovery_and_unlimited_retries(self):
        hw = FakeHardware()
        e = Engine(config, hw, watchdog_reset=True)
        self.assertEqual(e.fault, 'RESET_WATCHDOG')
        for attempt in range(8):
            since = e.fault_since
            e.tick(since + 29999, 1, 32700, 32695, 32705)
            self.assertEqual(hw.mode, 'off')
            e.tick(since + 30000, 1, 32700, 32695, 32705)
            e.tick(since + 30999, 1, 32700, 32695, 32705)
            self.assertIsNotNone(e.fault)
            e.tick(since + 31000, 1, 32700, 32695, 32705)
            self.assertIsNone(e.fault)
            self.advance(e, since + 31005, since + 35000)
            self.assertEqual(e.fault, 'TIMEOUT')

    def test_config_fault_never_retries(self):
        e, hw = self.engine(A_DIRECTION=0)
        self.advance(e, 0, 120000, step=100)
        self.assertIn('CONFIG', e.fault)
        self.assertFalse(hw.history)

    def test_console_bounded_and_never_emits_with_power(self):
        e, hw = self.engine()
        self.advance(e, 0, 850)
        for n in range(100):
            e.event(str(n))
        self.assertEqual(len(e.pending), config.CONSOLE_PENDING)
        e.flush_console(lambda msg: self.fail('Impresion durante marcha'))
        e.tick(855, 1, 25000, 24995, 25005)
        e.flush_console(lambda msg: self.fail('Impresion durante freno'))

    def test_tick_wrap_and_long_continuous_operation_without_files(self):
        period = 1 << 30
        diff = lambda a, b: (a - b + period // 2) % period - period // 2
        clock = Clock(period - 100, diff)
        e, hw = self.engine()
        with patch('builtins.open', side_effect=AssertionError('No archivos')):
            for elapsed in range(0, 3 * 3600 * 1000 + 1, 100):
                now = clock.update((period - 100 + elapsed) % period)
                e.tick(now, 1, 20000, 19995, 20005)
        self.assertEqual(clock.now, 10800000)
        self.assertEqual(e.control.state, 'DETENIDO')
        self.assertEqual(hw.monitor.level, 1)
        self.assertIsNone(e.fault)


class StopSimulation(BaseException):
    pass


class FakeMachine:
    WDT_RESET = 3
    pins = {}

    class Pin:
        OUT = 1
        def __init__(self, number, mode, value=0):
            self.number = number
            FakeMachine.pins[number] = value
        def value(self, value):
            FakeMachine.pins[self.number] = value

    class WDT:
        def __init__(self, timeout):
            self.timeout = timeout
        def feed(self):
            pass

    @staticmethod
    def reset_cause():
        return 1


class FakeTime:
    def __init__(self, end, step=5):
        self.now, self.end, self.step = 0, end, step
    def ticks_ms(self):
        return self.now
    @staticmethod
    def ticks_diff(a, b):
        return a - b
    def sleep_ms(self, duration):
        self.now += self.step
        if self.now > self.end:
            raise StopSimulation()


class RuntimeTests(unittest.TestCase):
    def test_real_hardware_adapter_keeps_interlocks_and_led_off(self):
        import importlib
        import sys
        pins, writes, irq = {}, [], []
        class Pin:
            OUT, IN, PULL_UP = 1, 0, 2
            def __init__(self, number, mode=None, pull=None, value=None):
                self.number = number
                if value is not None:
                    self.value(value)
            def value(self, value=None):
                if value is not None:
                    if value and self.number in (5, 18):
                        assert not pins.get(18 if self.number == 5 else 5, 0)
                    pins[self.number] = int(value)
                    writes.append((self.number, int(value)))
                return pins.get(self.number, 1)
            def on(self):
                self.value(1)
            def off(self):
                self.value(0)
            def irq(self, handler):
                irq.append(handler)
        class PWM:
            def __init__(self, pin):
                self.duty = 0
            def duty_u16(self, value):
                self.duty = value
            def freq(self, value):
                self.hz = value
        class ADC:
            def __init__(self, number):
                pass
            def read_u16(self):
                return 32700
        with patch.dict(sys.modules, {'machine': SimpleNamespace(Pin=Pin, PWM=PWM, ADC=ADC)}):
            module = importlib.import_module('pico_final.hardware')
            module = importlib.reload(module)
            hw = module.Hardware(config)
            self.assertEqual(hw.read(8), (1, 32700, 32700, 32700))
            e = Engine(config, hw)
            for now in range(0, 1251, 5):
                hall = 32700 if now < 1005 else 20000
                e.tick(now, 1, hall, hall - 5, hall + 5)
            self.assertEqual(pins[18], 1)
            for now in range(1255, 1701, 5):
                e.tick(now, 0, 20000, 19995, 20005)
            self.assertEqual(pins[18], 0)
            self.assertEqual(pins[5], 1)
            hw.stop()
            self.assertEqual((pins[5], pins[18], pins['LED']), (0, 0, 0))
            self.assertEqual(irq, [None])
            self.assertNotIn(('LED', 1), writes)

    def test_unexpected_exception_recovers_and_finally_stops(self):
        hw = FakeHardware()
        hw.sample = (1, 32700, 32695, 32705)
        clock = FakeTime(32500)
        messages = []
        original = hw.read
        def read(count):
            if clock.now == 850:
                raise RuntimeError('ADC simulado')
            return original(count)
        hw.read = read
        with patch('builtins.open', side_effect=AssertionError('No archivos')):
            with self.assertRaises(StopSimulation):
                run(config, FakeMachine, clock, lambda c: hw, messages.append)
        self.assertTrue(any('EXCEPCION' in s for s in messages))
        self.assertTrue(any('RECUPERACION' in s for s in messages))
        self.assertEqual(hw.mode, 'off')
        self.assertEqual(hw.monitor.level, 0)
        self.assertEqual(FakeMachine.pins['LED'], 0)

    def test_ctrl_c_cancels_without_retry(self):
        hw = FakeHardware()
        clock = FakeTime(40000)
        def read(count):
            raise KeyboardInterrupt()
        hw.read = read
        with self.assertRaises(StopSimulation):
            run(config, FakeMachine, clock, lambda c: hw, lambda s: None)
        self.assertFalse(hw.history)
        self.assertEqual(hw.mode, 'off')

    def test_ctrl_c_during_sleep_keeps_motor_disabled(self):
        hw = FakeHardware()
        hw.sample = (1, 32700, 32695, 32705)
        clock = FakeTime(40000)
        sleep = clock.sleep_ms
        count_at_cancel = []
        def interrupt(duration):
            sleep(duration)
            if clock.now == 900:
                count_at_cancel.append(len(hw.history))
                raise KeyboardInterrupt()
        clock.sleep_ms = interrupt
        with self.assertRaises(StopSimulation):
            run(config, FakeMachine, clock, lambda c: hw, lambda s: None)
        self.assertEqual(len(hw.history), count_at_cancel[0])
        self.assertEqual(hw.mode, 'off')


if __name__ == '__main__':
    unittest.main()
