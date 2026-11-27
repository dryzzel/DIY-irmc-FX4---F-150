# DIY IMRC / CMCV controller for Ford F-150

[Español](README.es.md) · [Documentation](docs/README.md) · [Hardware](docs/en/hardware.md) · [Install](docs/en/installation.md) · [Configuration](docs/en/configuration.md)

I built this controller to replace the burned-out circuit board in the intake
Charge Motion Control Valve actuator on my **2007 Ford F-150 FX4, 5.4 L 3V**.
I wanted to keep the original housing, gears and RS-365SH motor instead of buying
a complete replacement actuator.

The replacement uses a Raspberry Pi Pico, a TB6612FNG motor driver and an SS49E
Hall sensor to detect the two endpoint magnets. A PC817 reads the PCM command,
and an open-collector Monitor circuit reports confirmed opening back to the PCM.

As of **November 2026**, I've had the finished assembly installed and working
correctly for several weeks. During testing, my scanner recognized the actuation
and no fault codes appeared. I'm sharing the code and wiring so others can build
on this project. I've tested it on my truck; compatibility with other engines,
model years and actuator revisions still needs to be checked.

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

The firmware I use is **[`pico_final/`](pico_final/)**. Copy its five package
modules into `/pico_final/` on the Pico and copy its `main.py` to **`/main.py`**.
Do not flatten all files into the Pico root or mix them with the archived test
programs. The controller may move the motor automatically after power-up.

## Hardware boundaries

My setup uses two LM2596 buck modules (motor and logic), a common ground,
and both TB6612 channels wired together. This is a DIY repair with testing on
my truck. Automotive transient and temperature qualification are beyond the
testing documented here, and the driver rating must be evaluated for each build.
PWM and timeout are not current limiting.

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

I kept the earlier experiments and diagrams in `legacy/` and `docs/archive/`
to preserve the development work. Some show different wiring or omit the Monitor
stage, so use the current guides when building your own version. Device backups,
raw logs and local development files are excluded from the release.

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
