"""Create verified clean ZIPs without uploading files or accessing hardware."""
import ast
import hashlib
import json
import re
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from check_repo import check
from release_files import ROOT, FIRMWARE, source_paths


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def firmware_version():
    tree = ast.parse((ROOT / 'pico_final/config.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in node.targets):
            version = ast.literal_eval(node.value)
            if isinstance(version, str) and re.fullmatch(r'[A-Za-z0-9_.-]+', version):
                return version
    raise ValueError('No safe VERSION in config.py')


def make_zip(destination, files, kind, version):
    manifest = {
        'kind': kind, 'firmware_version': version, 'license': 'GPL-3.0-only',
        'files': {name: {'bytes': len(data), 'sha256': sha256(data)}
                  for name, data in sorted(files.items())},
    }
    payload = dict(files)
    payload['MANIFEST.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode('utf-8')
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity error')
        for name, data in payload.items():
            if archive.read(name) != data:
                raise RuntimeError('ZIP verification failed: ' + name)
    print('Verified {} ({} files)'.format(destination.name, len(payload)))


def main():
    if not check():
        return 1
    version = firmware_version()
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    source = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in source_paths()}
    firmware = {'pico_final/' + name: (ROOT / 'pico_final' / name).read_bytes() for name in FIRMWARE}
    firmware['main.py'] = (ROOT / 'pico_final/main.py').read_bytes()
    firmware['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
    firmware['INSTALL.txt'] = (
        'IMRC / CMCV ' + version + ' - GPL-3.0-only\n\n'
        'ENGLISH\nDisconnect motor VM before transfer. Back up existing device files.\n'
        'Disable the old automatic launcher and power-cycle to clear its watchdog.\n'
        'Copy the five .py files in pico_final/ to /pico_final/ on the Pico.\n'
        'Copy main.py to /main.py LAST. Do not run it during transfer.\n'
        'INSTALL.txt, LICENSE and MANIFEST.json are for the PC.\n'
        'The launcher starts automatically and may move the motor.\n'
        'Consult the bilingual hardware, calibration and commissioning guides in\n'
        'the matching source ZIP before enabling motor power on a new assembly.\n'
        'Reference values: PWM 40% -> 70%, 20 ms ramp, 3 s travel timeout,\n'
        '50 ms brake; no current limiting and unlimited fault recovery retries.\n\n'
        'ESPANOL\nDesconecta VM del motor antes de transferir. Respalda el Pico.\n'
        'Deshabilita el lanzador anterior y corta/reconecta alimentacion para\n'
        'eliminar su watchdog. Copia los cinco .py de pico_final/ a /pico_final/.\n'
        'Copia main.py a /main.py AL FINAL. No lo ejecutes durante la copia.\n'
        'INSTALL.txt, LICENSE y MANIFEST.json son para el PC.\n'
        'El arranque es automatico y puede mover el motor. Consulta las guias\n'
        'bilingues del ZIP de fuentes antes de alimentar un montaje nuevo.\n'
        'Valores: PWM 40% -> 70%, rampa 20 ms, timeout de marcha 3 s, freno 50 ms.\n'
        'Sin limite de corriente; reintentos de recuperacion ilimitados.\n'
    ).encode('utf-8')
    outputs = []
    for kind, files in (('source', source), ('firmware', firmware)):
        destination = out / ('imrc-{}-{}.zip'.format(version, kind))
        make_zip(destination, files, kind, version)
        outputs.append(destination)
    (out / 'SHA256SUMS').write_text(''.join(
        '{}  {}\n'.format(sha256(path.read_bytes()), path.name) for path in outputs
    ), encoding='utf-8', newline='\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
