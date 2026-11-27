# Permanent firmware / Firmware permanente — final-1

[Project overview](../README.md) · [Inicio en español](../README.es.md)

This is the permanent controller for the Pico + TB6612FNG + SS49E assembly,
including the PC817 command input and open-collector PCM Monitor. On 2026-11-27,
the owner reported weeks of correct installed operation on a 2007 F-150 FX4
5.4 L 3V. That report covers one vehicle and does not qualify other assemblies.

Copy the five package modules to `/pico_final/` on the device; copy this folder's
`main.py` to `/main.py` last. Disconnect motor VM during transfer. Calibration
values are specific to the reference assembly.

| Guide | English | Español |
| --- | --- | --- |
| Wiring | [Hardware](../docs/en/hardware.md) | [Hardware](../docs/es/hardware.md) |
| Upload and first run | [Installation](../docs/en/installation.md) | [Instalación](../docs/es/installation.md) |
| Settings | [Configuration](../docs/en/configuration.md) | [Configuración](../docs/es/configuration.md) |

Esta es la única versión permanente. El propietario informó funcionamiento
correcto durante semanas con el montaje instalado. Copia los cinco módulos a
`/pico_final/` y el lanzador a `/main.py` al final. Desconecta VM durante la copia.
Los umbrales y el sentido del motor deben verificarse en cada montaje nuevo.

There is no current, temperature or motor-supply measurement; recovery retries
are unlimited. The program creates no log files. / No hay medición de corriente,
temperatura ni alimentación del motor; los reintentos son ilimitados y no se
crean archivos de registro.

From the repository root / Desde la raíz del repositorio:

```sh
python -B -m unittest discover -s tests -p "test_*.py"
```

Licensed under [GPL-3.0-only](../LICENSE). / Licencia GPL versión 3.
