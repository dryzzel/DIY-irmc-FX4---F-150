# Publication and releases / Publicación

## Prepared content

The permanent firmware remains `final-1`; repository organization is not a new
motor-control revision. The owner reported installed operation for weeks on
2026-11-27. Current guides distinguish that report from host-test evidence.

Build and inspect the clean artifacts:

```sh
python tools/run_tests.py
python tools/check_repo.py
python tools/build_release.py
```

The firmware ZIP contains `/main.py` and `/pico_final/` in the correct device
layout, plus `INSTALL.txt`, `LICENSE` and a manifest for the PC. Only the launcher and
package Python files belong on the Pico. The source ZIP includes current docs,
tests and labeled archives, but excludes `.git`, backups, logs, virtual
environments, editor settings and Python bytecode. Each ZIP has a file manifest;
`dist/SHA256SUMS` contains the hashes of the ZIPs.

The project code uses [GPL-3.0-only](../LICENSE), selected by the owner. Keep the
license with both artifacts. The firmware ZIP is an installation convenience;
the matching source ZIP includes the code, tests and packaging scripts.

## Local validation — 2026-11-27

- 18 permanent-controller tests and 33 historical regression tests passed.
- All 27 preserved Python source files matched the pre-organization backup,
  including all six permanent firmware files. No motor settings were changed.
- Syntax and local documentation links passed the offline repository check.
- ZIP contents are verified byte-for-byte against their input, with SHA-256
  file manifests and archive hashes. The extracted source is tested separately.
- GitHub Actions is configured; it has not run remotely as part of this work.
- No Pico connection, upload, motor movement or new vehicle test was performed.

## Existing Git history needs a deliberate choice

The five existing commits were inspected during preparation. Eight historical
Python bytecode paths contain absolute local source filenames. Removing caches
from today's tree does **not** remove those copies from older commits. A targeted
text scan found no matching private-key/API-token patterns; this is not an
exhaustive secrets audit. Commit author names/emails also remain normal Git metadata.

For a publication without that history, use the **clean source ZIP** to create a
fresh repository with a fresh initial commit. Keep the old development repository
privately for provenance. Do not copy its `.git` directory into the new repository.
Alternatively, review and sanitize the old history before changing its visibility;
history rewriting and force-pushing are separate operations and were not performed.

An `origin` remote already exists. The connected GitHub app could not retrieve its
metadata during this work, so its visibility is not recorded as verified. Git
transport could read its HEAD. No push, release creation or visibility change was
performed by the repository preparation.

## Before publishing

- Preserve the selected GPL-3.0-only license and provide the corresponding source ZIP alongside firmware.
- Review both ZIP manifests and the current diagrams. Do not package the local
  backup directory or raw logs.
- Include photos or an as-built power-input drawing if the owner wants an exact
  reproduction guide; do not infer undocumented fuse/transient-protection values.
- Publish the clean source and firmware artifacts with the test results and the
  single-vehicle compatibility scope, without implying manufacturer endorsement.

## Español

Las versiones antiguas del historial incluyen cachés con rutas absolutas del PC.
La exclusión actual no borra esas versiones pasadas. El ZIP de código fuente
permite comenzar un repositorio público nuevo sin copiar `.git`, logs ni respaldos.
Conserva el repositorio de desarrollo como referencia privada. Si prefieres
publicar el historial existente, hay que revisarlo y limpiarlo por separado.

La licencia elegida es GPL-3.0-only; publica las fuentes junto al firmware. Esta preparación no cambió la visibilidad, no creó una
release y no hizo push. Los detalles no documentados de la protección de entrada
deben quedar identificados hasta disponer del esquema real del montaje.
