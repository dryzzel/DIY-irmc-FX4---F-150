# Contributing / Contribuir

Read [the current hardware guide](docs/en/hardware.md) and keep the tested firmware
under `pico_final/` separate from historical experiments in `legacy/`.

Contributions to the project code use the same [GPL-3.0-only license](LICENSE).
Only submit material you have the right to distribute under those terms.

Before proposing a change:

```sh
python tools/run_tests.py
python tools/check_repo.py
```

Describe the trigger, observed behavior, expected behavior and how the change was
checked. Identify host simulation, bench measurement and installed-vehicle testing
separately. Include relevant calibration values and firmware version. For a new
vehicle, provide the exact model year/engine and verified connector mapping.

Changes affecting direction, PWM, Hall thresholds, Monitor, retries or timeout
must explain the effect on movement and include a relevant regression test.
Do not treat the test suite as validation of an electrical modification.

Do not commit virtual environments, device backups, VINs, personal paths, device
serial numbers, complete road-test recordings or credentials. Share a small
redacted excerpt when it is needed to reproduce a problem.

New wiring diagrams should identify component pins by name, distinguish connector
view orientation, and agree with the English and Spanish guides. Put experimental
or superseded material under `docs/archive/` with a clear label.

## Español

Ejecuta las pruebas y la revisión antes de proponer cambios. Explica el problema,
el resultado esperado y qué se comprobó en simulación, banco o vehículo. Indica
modelo, motor, versión y calibración cuando sean relevantes. No publiques VIN,
respaldos completos, rutas personales, números de serie ni credenciales.

Los cambios que afectan movimiento o Monitor requieren una prueba de regresión
y una explicación de su efecto físico. Conserva las guías actuales coherentes
en ambos idiomas; los esquemas experimentales van al archivo histórico.
