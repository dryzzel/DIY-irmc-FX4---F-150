import unittest
from types import SimpleNamespace
import config
from controller import Controller


def settings(**changes):
    data = {k: v for k, v in vars(config).items() if k.isupper()}
    data.update(DRIVE_ENABLED=True, MONITOR_ENABLED=True, OPEN_END='A', A_DIRECTION=1,
                MOTION_TIMEOUT_MS=1000)
    data.update(changes)
    return SimpleNamespace(**data)


class ControlTests(unittest.TestCase):
    def simulate(self, c, start, end, cmd=1, hall=32000, vm=12):
        result = None
        for now in range(start, end + 1, 5):
            result = c.step(now, cmd, hall, vm)
        return result

    def test_defaults_do_not_move_or_assert_monitor(self):
        c = Controller(config)
        r = self.simulate(c, 0, 3000, hall=38600)
        self.assertEqual(r['state'], 'DIAGNOSTICO')
        self.assertEqual(r['direction'], 0)
        self.assertFalse(r['monitor'])

    def test_missing_calibration_latches_fault(self):
        c = Controller(settings(OPEN_END=None))
        r = self.simulate(c, 0, 1000)
        self.assertIn('OPEN_END', r['fault'])
        self.assertEqual(r['direction'], 0)

    def test_open_and_monitor_only_after_settle(self):
        c = Controller(settings())
        r = self.simulate(c, 0, 850)
        self.assertEqual(r['direction'], 1)
        self.assertFalse(r['monitor'])
        r = self.simulate(c, 855, 880, hall=38600)
        self.assertEqual(r['direction'], 0)
        self.assertFalse(r['monitor'])
        r = self.simulate(c, 885, 1100, hall=38600)
        self.assertEqual(r['state'], 'DETENIDO')
        self.assertTrue(r['monitor'])

    def test_close_releases_monitor_and_reverses_after_pause(self):
        c = Controller(settings())
        self.simulate(c, 0, 800, hall=38600)
        r = self.simulate(c, 805, 850, cmd=0, hall=38600)
        self.assertFalse(r['monitor'])
        self.assertEqual(r['direction'], 0)
        r = self.simulate(c, 855, 1150, cmd=0, hall=38600)
        self.assertEqual(r['direction'], 0)
        r = self.simulate(c, 1155, 1200, cmd=0, hall=38600)
        self.assertEqual(r['direction'], -1)
        r = self.simulate(c, 1205, 1450, cmd=0, hall=26600)
        self.assertEqual(r['state'], 'DETENIDO')
        self.assertFalse(r['monitor'])

    def test_timeout_persists_across_command_changes(self):
        c = Controller(settings())
        r = self.simulate(c, 0, 2000)
        self.assertEqual(r['fault'], 'TIMEOUT')
        r = self.simulate(c, 2005, 2600, cmd=0)
        self.assertEqual(r['fault'], 'TIMEOUT')
        self.assertEqual(r['direction'], 0)

    def test_invalid_hall(self):
        for bad in (0, 65535):
            c = Controller(settings())
            self.simulate(c, 0, 850)
            r = c.step(855, 1, bad, 12)
            self.assertEqual(r['fault'], 'HALL_INVALIDO')
            self.assertEqual(r['direction'], 0)

    def test_power_absent_at_boot_waits_then_stabilizes(self):
        c = Controller(settings())
        r = self.simulate(c, 0, 1000, vm=0)
        self.assertEqual(r['direction'], 0)
        self.assertIsNone(r['fault'])
        r = self.simulate(c, 1005, 1800)
        self.assertEqual(r['direction'], 0)
        r = self.simulate(c, 1805, 1850)
        self.assertEqual(r['direction'], 1)

    def test_power_loss_latches_after_start(self):
        c = Controller(settings())
        self.simulate(c, 0, 850)
        r = c.step(855, 1, 32000, 6)
        self.assertEqual(r['fault'], 'ALIMENTACION')
        self.assertEqual(r['direction'], 0)

    def test_mapping_can_be_reversed(self):
        c = Controller(settings(OPEN_END='B', A_DIRECTION=-1))
        r = self.simulate(c, 0, 850)
        self.assertEqual(r['direction'], 1)

    def test_noise_does_not_reverse(self):
        c = Controller(settings())
        self.simulate(c, 0, 850)
        for now in range(855, 950, 5):
            r = c.step(now, 1 - (now // 5) % 2, 32000, 12)
            self.assertEqual(r['direction'], 0)

    def test_position_loss_is_not_retried(self):
        c = Controller(settings())
        self.simulate(c, 0, 800, hall=38600)
        r = self.simulate(c, 805, 900, hall=32000)
        self.assertEqual(r['fault'], 'POSICION_PERDIDA')
        self.assertFalse(r['monitor'])

    def test_hysteresis_keeps_endpoint(self):
        c = Controller(settings())
        self.simulate(c, 0, 800, hall=38600)
        r = self.simulate(c, 805, 1000, hall=34500)
        self.assertEqual(r['position'], 'A')
        self.assertTrue(r['monitor'])

    def test_monitor_disabled_remains_off(self):
        c = Controller(settings(MONITOR_ENABLED=False))
        self.assertFalse(self.simulate(c, 0, 1000, hall=38600)['monitor'])

    def test_monitor_requires_fresh_settle_after_hall_glitch(self):
        c = Controller(settings())
        self.assertTrue(self.simulate(c, 0, 700, hall=38600)['monitor'])
        self.assertFalse(c.step(705, 1, 32000, 12)['monitor'])
        r = self.simulate(c, 710, 800, hall=38600)
        self.assertFalse(r['monitor'])
        self.assertEqual(r['direction'], 0)
        self.assertTrue(self.simulate(c, 805, 950, hall=38600)['monitor'])

    def test_monitor_requires_fresh_settle_after_command_glitch(self):
        c = Controller(settings())
        self.assertTrue(self.simulate(c, 0, 700, hall=38600)['monitor'])
        self.assertFalse(c.step(705, 0, 38600, 12)['monitor'])
        self.assertFalse(self.simulate(c, 710, 820, hall=38600)['monitor'])
        self.assertTrue(self.simulate(c, 825, 1000, hall=38600)['monitor'])


if __name__ == '__main__':
    unittest.main()
