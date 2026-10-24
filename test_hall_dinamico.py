import json
import os
import runpy
import tempfile
import types
import unittest
from unittest.mock import patch


class DynamicHallTests(unittest.TestCase):
    def run_learning(self, failure=None):
        clock = [0]
        hall = [32000]
        pins = {}
        class Pin:
            IN, OUT, PULL_UP = 0, 1, 2
            def __init__(self, n, *args, value=0):
                self.n, self.level = n, value
                pins[n] = self
            def value(self, v=None):
                if v is not None: self.level = int(v)
                return self.level
            def on(self): self.value(1)
            def off(self): self.value(0)
        class ADC:
            def __init__(self, n): pass
            def read_u16(self):
                if pins[5].level and pins[2].level != pins[3].level:
                    if failure == 'saturation': return 65535
                    if failure != 'timeout':
                        hall[0] += 5 if pins[2].level else -5
                return hall[0]
        class PWM:
            def __init__(self, p): pass
            def duty_u16(self, v): pass
        machine = types.SimpleNamespace(Pin=Pin, ADC=ADC, PWM=PWM)
        time = types.SimpleNamespace(ticks_ms=lambda:clock[0],
            ticks_diff=lambda a,b:a-b, sleep_ms=lambda t:clock.__setitem__(0,clock[0]+t))
        with patch.dict('sys.modules', machine=machine, time=time), patch('builtins.print'):
            ns=runpy.run_path('prueba_tb6612.py',run_name='hall_test')
            old=os.getcwd()
            with tempfile.TemporaryDirectory() as folder:
                try:
                    os.chdir(folder)
                    ns['probar_recorrido'](aprendizaje=True)
                    with open('hall_dinamico.json') as f: report=json.load(f)
                finally: os.chdir(old)
        self.assertEqual(pins[5].level,0)
        self.assertEqual(pins[18].level,0)
        return report

    def test_learns_two_ends_without_applying_configuration(self):
        report=self.run_learning()
        self.assertTrue(report['completo'])
        self.assertFalse(report['validado_para_control'])
        self.assertEqual(set(report['capturas']), {'centro','A','B'})
        self.assertEqual([x['destino'] for x in report['tramos']],['A','B'])
        self.assertTrue(all(x['curva'] for x in report['diagnosticos']))
        self.assertTrue(all(x['freno_ms']==50 for x in report['tramos']))

    def test_timeout_saves_moving_measurements_and_cancels_second_leg(self):
        report=self.run_learning('timeout')
        self.assertFalse(report['completo'])
        self.assertEqual(len(report['tramos']),1)
        self.assertEqual(report['tramos'][0]['motivo'],'TIMEOUT')
        self.assertTrue(report['diagnosticos'][0]['curva'])
        self.assertEqual(set(report['capturas']),{'centro'})

    def test_saturation_preserves_raw_evidence(self):
        report=self.run_learning('saturation')
        self.assertFalse(report['completo'])
        self.assertEqual(report['diagnosticos'][0]['crudo_max'],65535)
        self.assertEqual(len(report['diagnosticos']),1)


if __name__=='__main__': unittest.main()
