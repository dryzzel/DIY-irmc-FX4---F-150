# Releases / Publicación

[Documentation](README.md) · [Project](../README.md) · [Proyecto](../README.es.md)

## English

### Prepare a release

From the repository root, with Python 3.11 or later:

```sh
python tools/run_tests.py
python tools/check_repo.py
python tools/build_release.py
```

The tools run on the PC. They do not connect to a Pico, start the motor, upload
firmware, push commits or change repository visibility. GitHub Actions runs the
same checks and packages artifacts; its run must succeed separately on GitHub.

### Publish both packages

| Artifact in `dist/` | Contents and use |
| --- | --- |
| `imrc-final-1-firmware.zip` | `/main.py` and five modules under `/pico_final/`, ready for the device layout; `INSTALL.txt`, `LICENSE` and `MANIFEST.json` stay on the PC |
| `imrc-final-1-source.zip` | Source, tests, current documentation, tools and labeled development archives |
| `SHA256SUMS` | SHA-256 checksums of both ZIPs |

Each ZIP has a manifest of file sizes and SHA-256 hashes. Inspect it before
publishing. Keep the [GPL-3.0-only license](../LICENSE) with the code and provide
the matching source alongside the firmware. Do not upload backups or raw logs.

`final-1` is the firmware version in `pico_final/config.py`. A documentation-only
change can produce a new source ZIP with the same firmware version. Rebuild after
edits, and use the archive checksums plus a distinct Git tag/release label to
identify published artifacts. Do not silently replace an existing release ZIP.

### Choose the public Git history

The original development history contains Python caches with local source paths.
Deleting caches from the latest tree does not remove older copies. The
[dated review](en/project-review.md) records this finding.

For a fresh public history, extract the source ZIP into a new directory and create
a new repository there. Do not copy the development repository's `.git` folder.
The ZIP already excludes Git history, local backups, recordings and environments.
Keep the original repository privately for development provenance.

Publishing the existing history instead requires a separate history cleanup and
review. A normal commit or `.gitignore` change does not perform that cleanup.

### Release description

State the tested vehicle, firmware version, configuration changes and test
results. Distinguish PC simulations from bench and installed-vehicle results.
Link the current hardware guide, including any details still needed to reproduce
the assembly. Publish photos or an as-built schematic when available; avoid
inventing undocumented component values. Firmware changes require renewed
bench validation appropriate to the change before vehicle use.

## Español

### Preparar la publicación

Ejecuta los tres comandos anteriores desde la raíz con Python 3.11 o posterior.
Se ejecutan en el PC: no conectan el Pico, no mueven el motor, no cargan firmware
ni publican en GitHub. GitHub Actions realiza las mismas comprobaciones; su
ejecución remota debe verificarse por separado.

### Publicar ambos paquetes

El ZIP de firmware contiene `/main.py` y cinco módulos en `/pico_final/` con la
estructura del dispositivo. `INSTALL.txt`, `LICENSE` y `MANIFEST.json` son para
el PC. El ZIP de fuentes incluye código, pruebas, guías, herramientas e historia
de desarrollo etiquetada. `SHA256SUMS` permite comprobar ambos ZIP.

Conserva la licencia GPL-3.0-only y entrega las fuentes correspondientes junto
al firmware. Revisa los manifiestos; no incluyas respaldos ni logs completos.
`final-1` identifica el firmware. Un cambio solo documental puede generar otro
ZIP con la misma versión: vuelve a empaquetar y usa un tag/nombre de publicación
distinto y los hashes para identificarlo. No reemplaces silenciosamente un ZIP
ya publicado.

### Elegir el historial público

El historial original contiene cachés con rutas locales. Borrarlas del árbol
actual no elimina las copias antiguas; consulta el [informe](es/project-review.md).
Para empezar limpio, extrae el ZIP de fuentes en otra carpeta y crea allí un
repositorio nuevo, sin copiar `.git`. Conserva el repositorio anterior en privado.
Publicar su historial requiere limpiarlo y revisarlo por separado.

### Describir la versión

Indica vehículo probado, versión, cambios de configuración y resultados. Distingue
simulación en PC, banco y uso instalado. Enlaza las guías actuales y sus detalles
pendientes de reproducción. Añade fotos o el esquema real cuando estén disponibles;
no inventes componentes. Los cambios de firmware requieren comprobación de banco
adecuada antes de usarlos en el vehículo.
