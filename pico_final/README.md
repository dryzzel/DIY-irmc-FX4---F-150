# Permanent firmware / Firmware permanente — final-1

[Project overview](../README.md) · [Inicio en español](../README.es.md)

This is the firmware I use in my 2007 Ford F-150 FX4 5.4 L 3V. It controls the
Pico + TB6612FNG + SS49E assembly, including the PC817 command input and
open-collector PCM Monitor. The [project introduction](../README.md) describes
the build and my experience using it.

Copy the five package modules to `/pico_final/` on the device; copy this folder's
`main.py` to `/main.py` last. Disconnect motor VM during transfer. Calibration
values are specific to the reference assembly.

| Guide | English | Español |
| --- | --- | --- |
| Wiring | [Hardware](../docs/en/hardware.md) | [Hardware](../docs/es/hardware.md) |
| Upload and first run | [Installation](../docs/en/installation.md) | [Instalación](../docs/es/installation.md) |
| Settings | [Configuration](../docs/en/configuration.md) | [Configuración](../docs/es/configuration.md) |

Este es el firmware que uso en mi F-150. La [introducción](../README.es.md)
describe el montaje y mi experiencia usándolo. Copia los cinco módulos a
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

## Module map / Mapa de módulos

| File | Responsibility / Responsabilidad |
| --- | --- |
| `main.py` | Disable outputs, then start the runtime / Apagar salidas e iniciar el programa |
| `config.py` | Effective settings / Ajustes efectivos |
| `controller.py` | Command, Hall, destination and travel budget / Orden, Hall, destino y presupuesto de marcha |
| `runtime.py` | Brake, Monitor interlocks, recovery, watchdog and console / Freno, Monitor, recuperación, watchdog y consola |
| `hardware.py` | GPIO, PWM and ADC access / Acceso a GPIO, PWM y ADC |
| `__init__.py` | Package marker / Identificación del paquete |

The launcher imports this package explicitly. Archived root-level modules are
not used. / El lanzador importa este paquete explícitamente; no utiliza los
módulos antiguos de la raíz.
