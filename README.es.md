# Controlador DIY IMRC / CMCV para Ford F-150

[English](README.md) · [Documentación](docs/README.md) · [Hardware](docs/es/hardware.md) · [Instalación](docs/es/installation.md) · [Configuración](docs/es/configuration.md)

Hice este controlador para reemplazar la placa quemada del actuador CMCV de
la admisión de mi **Ford F-150 FX4 2007, motor 5.4 L 3V**. Quería conservar
la carcasa, los engranajes y el motor RS-365SH originales, sin tener que comprar
el actuador completo.

El reemplazo usa un Raspberry Pi Pico, un driver TB6612FNG y un sensor Hall SS49E
para detectar los dos imanes de los extremos. Un PC817 lee la orden de la PCM,
y un circuito Monitor de colector abierto devuelve la confirmación de apertura.

A **noviembre de 2026**, ya tengo el montaje terminado, instalado y funcionando
correctamente desde hace varias semanas. Durante las pruebas, el escáner reconoció
la actuación y no aparecieron códigos de falla. Comparto el código y el cableado
para que otros puedan aprovechar el proyecto. Lo he probado en mi camioneta;
la compatibilidad con otros motores, años y revisiones del actuador debe comprobarse.

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

El programa que uso está en **[`pico_final/`](pico_final/)**. Sus cinco módulos
de paquete van en `/pico_final/` del Pico y su lanzador `main.py` va en **`/main.py`**.
No copiar todos los módulos sueltos a la raíz ni mezclarlos con las pruebas
históricas. El motor puede actuar automáticamente después de encender.

## Límites del montaje

Mi montaje utiliza dos LM2596, tierra común y los dos canales del TB6612
conectados juntos. Es una reparación DIY probada en mi camioneta. La calificación
automotriz de transitorios y temperatura queda fuera de las pruebas documentadas
aquí, y la capacidad del driver debe evaluarse en cada montaje. PWM y timeout
no limitan la corriente.

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

Conservé los experimentos y diagramas anteriores en `legacy/` y `docs/archive/`
como parte del desarrollo. Algunos muestran otro cableado o no incluyen Monitor;
para reproducir el montaje, sigue las guías actuales. Los respaldos del Pico,
logs completos y archivos locales de desarrollo quedan fuera de la publicación.

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
