# Repository review — 27 November 2026

[Documentation](../README.md) · [Español](../es/project-review.md)

## Result and scope

The project has a working installed assembly and a dedicated permanent firmware
package. The confusion came mainly from documentation voice, overlapping entry
points and development revisions that looked like current instructions. This
review corrected those presentation issues without changing the motor controller.

The review covers the current source tree, firmware responsibilities, configuration,
documentation in both languages, tests, release packaging and the previously
identified Git-history issue. It is a repository review, not a new vehicle test,
electrical certification or exhaustive security audit.

The installed-build results in the project introduction are my experience with
my 2007 F-150 FX4 5.4 L 3V. The local checks below are separate software evidence.

## Findings and changes

| Finding | Why it was confusing | Resolution |
| --- | --- | --- |
| An external narrator described the project | “The owner reported” made my build story sound secondhand | Both main READMEs, the firmware README, hardware guides and changelog now use first person for firsthand results |
| Technical instructions mixed with cleanup-session notes | GitHub connection details and descriptions of work performed distracted from installation | The release guide now describes a repeatable process; dated findings belong in this report |
| Several files appeared to be the final design | Archived `ESQUEMA_FINAL` files and older `main.py` files looked like alternatives | The documentation index identifies one current firmware package and one current set of wiring guides; archive and legacy catalogs explain the old names |
| Duplicate test bundles were unexplained | Five files in `legacy/pico_prueba_camioneta/` match files in `legacy/`, but their launchers differ | Documented the device-copy snapshot and retained it for history; no second maintained firmware branch is implied |
| Missing documentation sounded like an unfinished installation | Old “vehicle test pending” statements conflicted with weeks of installed operation | Current hardware guides separate missing reproduction details from completed use; archive statements are explicitly historical |
| Test counts hid scope | “51 tests” could be read as 51 final-controller tests | Validation is described as 18 permanent-controller tests plus 33 historical regressions |
| Text-file policies were inconsistent | `.editorconfig` requested LF, but some Git-managed text files could use platform defaults | Set the Git default to LF for text while retaining binary exceptions; no firmware source was rewritten in this review |
| Removing caches did not remove their history | A clean working tree could be mistaken for a clean historical release | Kept the source-export path and explained the separate history decision in the release guide |

There is now a documented writing convention: first person for the project story,
direct instructions for installation, neutral technical wording for behavior,
and dated review notes for audit findings. English and Spanish entry points follow
the same structure.

## Current project structure

| Location | Status | Intended reader |
| --- | --- | --- |
| [Root introduction](../../README.md) | Current project story and starting point | Everyone |
| [Documentation index](../README.md) | Current reading order | Builders and contributors |
| [pico_final](../../pico_final/README.md) | Sole permanent firmware source | Installers and firmware maintainers |
| [Hardware](hardware.md), [configuration](configuration.md), [installation](installation.md) | Current instructions | Someone reproducing the build |
| [tests](../../tests/) | Permanent-controller simulations | Firmware contributors |
| [examples](../../examples/README.md) | Optional isolated Monitor test | Bench troubleshooting |
| [legacy](../../legacy/README.md) | Preserved experiments and logger | Historical diagnosis |
| [archive](../archive/README.md) | Superseded drawings and notes | Development reference |
| [tools](../../tools/) | PC-only checks and packaging | Release maintainers |

No further mass renaming or deletion was needed. Preserving historical bundles
keeps old test results understandable; clearer entry points prevent them from
competing with the installed program. Old files are not current install targets.

## Firmware review

The launcher first disables GP5, GP18 and the built-in LED, then imports
`pico_final.runtime`. The module responsibilities are distinct:

- `config.py`: effective calibration, pins, timing and feature switches.
- `controller.py`: command qualification, Hall classification, destination,
  settling and accumulated powered-travel budget.
- `runtime.py`: applied motor/brake state, Monitor gating, recovery, watchdog,
  monotonic clock extension and bounded console events.
- `hardware.py`: GPIO, PWM, ADC reads, brake and stop operations.

The important configuration remains:

| Behavior | Effective value |
| --- | --- |
| Command | GP15=0 closes; GP15=1 opens |
| End mapping | A is high Hall/closed; B is low Hall/open; `A_DIRECTION=1` |
| PWM | 40% initial, 70% running, 20 ms ramp, 20 kHz |
| Travel budget | 3000 ms powered motion per confirmed destination |
| Pause and brake | 300 ms start/reversal/resume pause; 50 ms endpoint brake |
| Hall A | Enter at ≥40000; retain above 35000 |
| Hall B | Enter at ≤26000; retain below 31300 |
| Valid Hall | Every raw sample strictly between 2000 and 63500 |
| Filtering | Command 50 ms; Hall classification 30 ms; settling 150 ms |
| Startup | 500 ms qualification; no extra five-second delay |
| Recovery | 30-second wait, then one second of valid Hall and unchanged command |
| Monitor | Only confirmed, settled opening with motor and brake inactive |
| Indicators | Built-in LED off; external command/fault LEDs retained |
| Recording | No final-firmware log files; bounded RAM console queue |

A new confirmed destination renews the timeout; noise and pauses do not. Brake
time is not powered-travel time. A/B identify Hall polarity ranges, while the
direction sign identifies motor wiring; changing `OPEN_END` does not by itself
require reversing `A_DIRECTION`.

Raw out-of-range readings stop control even if their average looks plausible.
Loop faults enter recovery; invalid configuration stays blocked. Recovery is
unlimited and does not measure motor current or diagnose a jam. A released/high
Monitor during movement or failure is not independent proof of physical closure.

The recovery claim applies to the running control loop and the explicit watchdog
reset path. Module imports and initial hardware construction occur before that
protected loop; missing files and boot-time setup failures should not be assumed
to follow the same recovery path. This review did not alter those paths.

## Hardware and reproduction gaps

The current guide consolidates the connector mapping, common ground, separated
5 V/12 V positive supplies, synchronized driver connections, Hall filter and
open-collector Monitor. It records the approximately 12 V/high and 0 V/low
Monitor measurements with the PCM connected. The PCM supplies the high level.

For another builder to reproduce the physical assembly precisely, these details
still need to be supplied from the actual installation:

| Missing detail | What it would resolve |
| --- | --- |
| Exact input-protection circuit and fuse rating | The protected-input block is currently descriptive, not a complete component-level design |
| Exact module/sensor/transistor variants | Similar modules and markings can have different pin arrangements |
| Photos, connector views, mounting and magnet/sensor spacing | Calibration and polarity must match the physical mechanism |
| Complete as-built drawing | The archive includes revisions and an illustrative image, not one definitive final schematic |
| Tested MicroPython version | The target board is documented; the exact installed interpreter build is not pinned |

These are documentation gaps. The current installation is already in use.
No claims of broad vehicle compatibility, transient qualification or driver
current margin were added. No new components were chosen or substituted.

## Validation and its limits

- **18 permanent-controller tests:** timing, stable commands, travel budget,
  brake/Monitor interlocks, Hall validity, position loss, recovery, configuration
  blocking, console bounds, clock wraparound, hardware adapter and cancellation.
- **33 historical tests:** earlier controller, logger and manual-test regressions.
- **Repository checks:** Python syntax without hardware imports, local Markdown
  file links, license presence and a targeted private-path/token-pattern scan.
- **Source preservation:** all six `pico_final/*.py` files still match the
  pre-organization backup byte for byte; Git shows no firmware-source changes.
- **Packaging:** both ZIPs are read back and verified; the source export is
  extracted separately and checked/tested. Manifests record actual file hashes.

Host simulations cannot prove motor current, electrical noise immunity, PCM
acceptance or operation under a different mechanical load. The text scan is not
a complete credential scan or binary-image metadata audit. Local link checks
do not verify every external URL. GitHub Actions is configured but a remote run
has not been observed during this review. No board was connected or flashed.

## Publication status

GPL-3.0-only is selected and included. The source and firmware packages preserve
the license and include SHA-256 manifests. Generated ZIPs, raw recordings,
virtual environments and private Pico backups stay out of Git.

The first cleanup identified local source paths in eight Python bytecode files
within the original five commits. Removing caches in a later commit cannot
remove those historical copies. A fresh repository from the clean source ZIP
avoids carrying those commits; publishing the original history requires a
separate cleanup decision. No history rewriting, force push or visibility change
was performed in this review.

The release builder uses the firmware version for filenames. Documentation-only
changes therefore need rebuilt checksums and a distinct release label when
published. The [release guide](../RELEASING.md) now explains this explicitly.

## Next steps

The documentation and organization corrections are implemented. The remaining
publication work is to choose the public-history route, run the checks on the
chosen repository and publish a tagged source/firmware pair. Exact hardware
reproduction details can be added from the installed assembly without changing
its working firmware. None of these remaining steps requires retuning the motor
simply to make the repository easier to understand.
