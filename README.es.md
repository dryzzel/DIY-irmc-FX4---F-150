# Controlador DIY IMRC / CMCV para Ford F-150

[English](README.md) · [Hardware](docs/es/hardware.md) · [Instalación](docs/es/installation.md) · [Configuración](docs/es/configuration.md)

Controlador con Raspberry Pi Pico para sustituir la placa averiada del actuador
CMCV de la admisión. Reutiliza carcasa, engranajes y motor RS-365SH originales.
Lee la orden de la PCM mediante un PC817, detecta los extremos con un SS49E,
acciona un TB6612FNG y devuelve la confirmación de apertura por una etapa Monitor
de colector abierto.

**Vehículo probado:** Ford F-150 FX4 2007 del propietario, motor 5.4 L de 3 válvulas.
El **27 de noviembre de 2026**, el propietario confirmó que terminó el montaje,
lo instaló y llevaba semanas funcionando correctamente. En pruebas anteriores
también indicó que el escáner reconocía la actuación sin códigos de falla.
Es experiencia de un montaje; no confirma compatibilidad con otros motores,
años ni revisiones del actuador.

## Funcionamiento

- GP15 bajo ordena cerrar; GP15 alto ordena abrir, después del filtro de estabilidad.
- Corta al detectar el extremo Hall y aplica freno eléctrico durante 50 ms.
- PWM inicial 40%, final 70%, con rampa de 20 ms.
- Timeout de 3 segundos de marcha por nueva orden estable; no se renueva por ruido
  ni pausas.
- Monitor activo solo con apertura confirmada y asentada, sin marcha ni freno.
- Ante fallo, apaga salidas, espera 30 segundos y exige un segundo de Hall válido
  y comando estable antes de reanudar el control.
- Funciona continuamente sin archivos de registro. Consola acotada en RAM,
  LED integrado apagado e indicadores externos de orden/recuperación.

## Por dónde empezar

1. Revisar [componentes, conector y cableado](docs/es/hardware.md).
2. Medir los extremos, confirmar el sentido y revisar la [configuración](docs/es/configuration.md).
3. Seguir la [instalación y puesta en marcha](docs/es/installation.md).

El programa permanente está en **[`pico_final/`](pico_final/)**. Sus cinco módulos
de paquete van en `/pico_final/` del Pico y su lanzador `main.py` va en **`/main.py`**.
No copiar todos los módulos sueltos a la raíz ni mezclarlos con las pruebas
históricas. El motor puede actuar automáticamente después de encender.

## Límites del montaje

La referencia utiliza dos LM2596, tierra común y los dos canales del TB6612
conectados juntos como en este montaje. No es un diseño automotriz certificado.
No hay validación publicada de transitorios, temperatura ni capacidad universal
de corriente. PWM y timeout no limitan la corriente.

No se mide corriente, temperatura ni tensión VM. Los reintentos son ilimitados:
un atasco persistente puede causar nuevos esfuerzos. Los umbrales pertenecen a
este sensor y montaje de imanes; hay que medirlos en otra unidad. La guía de
hardware identifica los detalles de protección de alimentación no documentados.

## Organización

| Carpeta | Contenido |
| --- | --- |
| `pico_final/` | Firmware permanente y configuración comentada |
| `tests/` | Simulaciones del controlador final en el PC |
| `docs/en/`, `docs/es/` | Guías actuales en inglés y español |
| `examples/` | Prueba aislada de Monitor por BOOTSEL |
| `legacy/` | Prototipos, registrador temporal y sus pruebas |
| `docs/archive/` | Diagramas anteriores y notas de desarrollo |
| `tools/` | Pruebas, revisión del repositorio y paquetes de publicación |

Los respaldos del Pico, entornos locales, logs y cachés no se publican. Los
diagramas antiguos están archivados porque algunos muestran otra revisión o
no incluyen Monitor.

## Desarrollo

Con Python 3.11+; no hace falta conectar el Pico:

```sh
python tools/run_tests.py
python tools/check_repo.py
python tools/build_release.py
```

Se generan un ZIP del firmware y otro del código fuente limpio en `dist/`, con
manifiestos SHA-256. Las herramientas no cargan el Pico ni publican en GitHub.
Consulta [contribuciones](CONTRIBUTING.md), [cambios](CHANGELOG.md) y
[preparación de publicación](docs/RELEASING.md).

## Licencia

El código del proyecto se publica bajo **GNU GPL versión 3 únicamente**
(`SPDX-License-Identifier: GPL-3.0-only`). Consulta [LICENSE](LICENSE).
Las versiones modificadas que se distribuyan deben cumplir la GPL, incluida
la entrega del código fuente correspondiente. No se ofrece garantía. Los
datasheets de terceros se enlazan; no se incluyen ni se cambia su licencia.
