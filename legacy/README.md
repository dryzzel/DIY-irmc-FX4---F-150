# Archived development firmware / Firmware de desarrollo archivado

These are the original experiments, test recorder and regression tests, preserved
with their existing settings. **They are not the installed release.** Some scripts
can move the motor, write logs, or use older pin/calibration assumptions.

Use [pico_final](../pico_final/README.md) for the permanent controller. Do not mix
files from this directory with that package. In particular, the root-level
`config.py` and `main.py` here belong to an early prototype.

The `pico_prueba_camioneta/` subdirectory is the former autonomous test recorder.
It has a time/storage limit and a different fault policy. It remains here for
reproducing historical tests, not as the installation source.

Run the old host simulations in their own process and working directory:

```sh
cd legacy
python -B -m unittest discover -s . -p "test_*.py"
```

Or run both suites from the repository root with `python tools/run_tests.py`.
This separation prevents the old `config` and `controller` modules from shadowing
the final package. Hardware testing notes are in [the document archive](../docs/archive/README.md).

## Español

Se conservan experimentos y pruebas históricas con sus valores originales.
**No son la versión instalada.** Para instalar usa `pico_final/`; no mezcles sus
archivos con estos. Los scripts de aquí pueden mover el motor, crear registros
o usar otra calibración. El lanzador antiguo y el registrador de camioneta no
sustituyen al programa final.
