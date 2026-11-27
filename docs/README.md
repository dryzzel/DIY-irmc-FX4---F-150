# Documentation / Documentación

[Project / Proyecto](../README.md) · [Inicio en español](../README.es.md)

## Build and install / Montaje e instalación

Read these guides in order. They describe the permanent `pico_final/` program.
Lee estas guías en orden; corresponden al programa permanente `pico_final/`.

| Step / Paso | English | Español |
| --- | --- | --- |
| 1. Parts, connector and wiring / Componentes, conector y cableado | [Hardware](en/hardware.md) | [Hardware](es/hardware.md) |
| 2. Direction, endpoints and settings / Sentido, extremos y ajustes | [Configuration](en/configuration.md) | [Configuración](es/configuration.md) |
| 3. Copy files and verify a new build / Copiar archivos y verificar otro montaje | [Installation](en/installation.md) | [Instalación](es/installation.md) |

The exact settings live in [config.py](../pico_final/config.py). The
[module map](../pico_final/README.md) explains how the six firmware files fit together.
Los ajustes efectivos están en `config.py`; el mapa explica la función de cada módulo.

## Development and maintenance / Desarrollo y mantenimiento

| Topic / Tema | Document / Documento |
| --- | --- |
| Contributing and testing / Contribuciones y pruebas | [CONTRIBUTING](../CONTRIBUTING.md) |
| Firmware and source ZIPs / ZIP del firmware y fuentes | [Releasing / Publicación](RELEASING.md) |
| Changes / Cambios | [Changelog](../CHANGELOG.md) |
| Repository review, fixes and remaining gaps / Revisión, cambios y pendientes | [English report](en/project-review.md) · [Informe en español](es/project-review.md) |

## Optional tests and history / Pruebas opcionales e historia

- [Monitor BOOTSEL example / Ejemplo Monitor BOOTSEL](../examples/README.md):
  isolated electrical test; separate from the automatic controller / prueba
  eléctrica aislada; separada del controlador automático.
- [Legacy programs / Programas antiguos](../legacy/README.md): earlier controller,
  manual menu and temporary logger / controlador anterior, menú y registrador temporal.
- [Archived drawings and notes / Planos y notas anteriores](archive/README.md):
  preserved development revisions, including files with “FINAL” in their old names /
  revisiones de desarrollo, incluso archivos que llevan «FINAL» en el nombre antiguo.

The archive does not override the current guides. / El archivo histórico no
sustituye las guías actuales.
