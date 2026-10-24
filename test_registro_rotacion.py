import ast
import json
import os
from pathlib import Path
import tempfile
import unittest


class RotationTests(unittest.TestCase):
    def setup_logger(self, folder, slots=8):
        # Registro no depende del hardware; cargar la clase sin inicializar pines.
        tree=ast.parse(Path('prueba_camioneta.py').read_text(encoding='utf-8'))
        node=next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=='Registro')
        env={'os':os,'json':json,'DIRECTORIO':folder,'MAX_ARCHIVOS':slots,
             'MAX_BYTES':1900,'MAX_PENDIENTES':256}
        # El directorio se crea en el test y listdir() se usa solo en __init__.
        original=os.listdir
        from unittest.mock import patch
        with patch('os.listdir',side_effect=lambda path=None: [folder] if path is None else original(path)):
            exec(compile(ast.Module(body=[node],type_ignores=[]),'registro','exec'),env)
            return env['Registro']()

    def rows(self, folder):
        result=[]
        for p in sorted(Path(folder).glob('*.jsonl')):
            self.assertLessEqual(p.stat().st_size,1900)
            result.extend(json.loads(line) for line in p.read_text().splitlines())
        return result

    def test_rotation_preserves_events_and_feeds_between_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            log=self.setup_logger(folder)
            ticks=[]
            log.heartbeat=lambda:ticks.append(1)
            for n in range(12): log.add({'evento':'ESTADO','ms':n,'datos':'x'*200})
            log.flush()
            log.finish({'evento':'FIN','motivo':'FIN_TIEMPO','ms':12})
            rows=self.rows(folder)
            self.assertEqual([r['ms'] for r in rows if r['evento']=='ESTADO'],list(range(12)))
            self.assertTrue(any(r['evento']=='CONTINUACION' for r in rows))
            self.assertEqual(rows[-1]['evento'],'FIN')
            self.assertGreater(len(ticks),12)

    def test_full_slots_keep_room_for_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            log=self.setup_logger(folder,slots=1)
            for n in range(12): log.add({'evento':'ESTADO','ms':n,'datos':'x'*200})
            with self.assertRaisesRegex(OSError,'REGISTROS_LLENO'): log.flush()
            log.finish({'evento':'FIN','motivo':'REGISTROS_LLENO','ms':12})
            rows=self.rows(folder)
            self.assertEqual(rows[-1]['motivo'],'REGISTROS_LLENO')
            self.assertGreater(rows[-1]['pendientes_descartados'],0)

    def test_existing_recordings_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'prueba_01.jsonl'
            p.write_text('original')
            log=self.setup_logger(folder)
            self.assertTrue(log.path.endswith('prueba_02.jsonl'))
            self.assertEqual(p.read_text(),'original')

if __name__=='__main__': unittest.main()
