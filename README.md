# DIY IMRC / CMCV controller for Ford F-150

[Español](README.es.md) · [Hardware](docs/en/hardware.md) · [Install](docs/en/installation.md) · [Configuration](docs/en/configuration.md)

A Raspberry Pi Pico replacement controller for a failed intake Charge Motion
Control Valve actuator PCB. It reuses the original housing, gears and RS-365SH
motor, reads the PCM command through a PC817, detects the two endpoints with an
SS49E Hall sensor, and drives a TB6612FNG. An open-collector Monitor stage reports
confirmed opening back to the PCM.

**Tested vehicle:** the owner's 2007 Ford F-150 FX4, 5.4 L 3-valve engine.
On **2026-11-27**, the owner reported that the finished hardware was installed and
had been operating correctly for weeks. Earlier testing also reported scanner
recognition of actuation without fault codes. This is experience with one build;
compatibility with other engines, model years or actuator revisions is unverified.

## What the permanent firmware does

- Follows a stable PCM command: GP15 low closes, high opens.
- Stops at calibrated Hall endpoints and applies a 50 ms electrical brake.
- Uses 40% initial PWM, 70% running PWM and a 20 ms ramp.
- Allows 3 seconds of powered travel for each new stable command. Noise and
  pauses do not renew the timeout.
- Asserts Monitor only after the open endpoint is confirmed and settled, with
  the motor and brake inactive.
- After a fault, disables the outputs, waits 30 seconds, and requires one second
  of valid Hall readings and a stable command before restarting control.
- Runs continuously with no log files. Console events use bounded RAM; the
  built-in LED stays off. External LEDs indicate the command or recovery state.

## Start here

1. Check the [connector, component list and wiring](docs/en/hardware.md).
2. Confirm your sensor positions, motor direction and [configuration](docs/en/configuration.md).
3. Follow the [installation and commissioning guide](docs/en/installation.md).

The installed firmware is **[`pico_final/`](pico_final/)**. Copy its five package
modules into `/pico_final/` on the Pico and copy its `main.py` to **`/main.py`**.
Do not flatten all files into the Pico root or mix them with the archived test
programs. The controller may move the motor automatically after power-up.

## Hardware boundaries

The reference uses two LM2596 buck modules (motor and logic), a common ground,
and both TB6612 channels wired together as used in this build. It is not a
manufacturer-qualified automotive design. The repository does not establish
load-dump/transient compliance, temperature qualification or a universally safe
driver current rating. PWM and timeout are not current limiting.

There is no motor-current, temperature or VM-voltage measurement. Recovery retries
are unlimited, so a persistent jam can cause repeated attempts. Endpoint thresholds
belong to this assembly and must be measured for another sensor/magnet placement.
See the hardware guide for the power-input details that remain unspecified.

## Repository layout

| Path | Purpose |
| --- | --- |
| `pico_final/` | Permanent MicroPython controller and documented configuration |
| `tests/` | Host-side simulations for the permanent controller |
| `docs/en/`, `docs/es/` | Current hardware, installation and configuration guides |
| `examples/` | Isolated BOOTSEL Monitor test, not the normal program |
| `legacy/` | Earlier experiments, temporary logger and their regression tests |
| `docs/archive/` | Superseded diagrams and development notes |
| `tools/` | Test runner, repository checks and release packaging |

Local virtual environments, device backups, test recordings and Python bytecode
are excluded. Historical diagrams are explicitly archived because they can show
different wiring or omit the Monitor stage.

## Development

Host tests use Python 3.11+ and the standard library; a Pico is not required:

```sh
python tools/run_tests.py
python tools/check_repo.py
python tools/build_release.py
```

The release builder creates a firmware ZIP and a clean source ZIP in `dist/`,
with SHA-256 manifests. It does not connect to hardware or publish to GitHub.
Read [contributing](CONTRIBUTING.md), [changes](CHANGELOG.md) and
[release preparation](docs/RELEASING.md) before publishing.

## License

The project code is licensed under **GNU GPL version 3 only**
(`SPDX-License-Identifier: GPL-3.0-only`). See [LICENSE](LICENSE).
Distributed modified versions must follow the GPL, including its corresponding
source requirements. No warranty is provided. Third-party datasheets are linked,
not bundled or relicensed.
