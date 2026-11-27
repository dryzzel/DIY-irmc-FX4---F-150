# Installation and commissioning

[Home](../../README.md) · [Español](../es/installation.md)

The firmware targets the original RP2040 Raspberry Pi Pico running MicroPython.
There are no third-party Python modules to install on the device. Host tests use
CPython 3.11+ and do not install or execute firmware on a connected Pico.

## Prepare the assembly

Review [hardware](hardware.md) and [configuration](configuration.md) first. Disconnect
motor VM while copying files or changing wiring. When programming via USB, use the
power arrangement described in the hardware guide; maintain the common driver ground.
The release has `DRIVE_ENABLED=True` and can act automatically when started.

If another program already runs as `/main.py`, stop and disable that launcher with
VM disconnected before replacing files. A running watchdog can reset the board
even after Ctrl+C. Power-cycle with the old autostart disabled before file transfer;
an editor's Stop button alone does not disable a hardware watchdog.

Install the official [MicroPython firmware for RPI_PICO](https://micropython.org/download/RPI_PICO/)
if the device does not already run a suitable RP2040 MicroPython build. Reflashing
or replacing files is not a substitute for backing up the files you want to keep.

## Exact file layout

The repository and the Pico have different launcher locations:

| Repository source | Pico destination |
| --- | --- |
| `pico_final/main.py` | `/main.py` |
| `pico_final/__init__.py` | `/pico_final/__init__.py` |
| `pico_final/config.py` | `/pico_final/config.py` |
| `pico_final/controller.py` | `/pico_final/controller.py` |
| `pico_final/hardware.py` | `/pico_final/hardware.py` |
| `pico_final/runtime.py` | `/pico_final/runtime.py` |

```text
Pico filesystem
├── main.py
└── pico_final/
    ├── __init__.py
    ├── config.py
    ├── controller.py
    ├── hardware.py
    └── runtime.py
```

In Thonny, select the MicroPython Raspberry Pi Pico interpreter and the correct
serial device. Use its Files view to create `/pico_final/`, copy the five package
modules there, and save the launcher as `/main.py` **last**. The equivalent firmware
ZIP already has this layout; `INSTALL.txt`, `LICENSE` and `MANIFEST.json` are for the PC and
are not required on the Pico.

For command-line users, `python -m pip install mpremote` installs the transfer tool
on the PC. `mpremote connect list` lists ports. Use `connect YOUR_PORT resume` for
access without an automatic soft reset. Do not assume a particular COM number or
that a connection leaves an already running motor controller untouched.

The permanent program imports `pico_final.config`, not an old root `/config.py`.
Change the package configuration on the PC, copy it to the same package path on
the Pico, and restart when ready. Local edits alone do not update the board.

## First run on a new assembly

1. Confirm ground, supply voltages and Monitor output with motor VM disconnected.
   The optional [BOOTSEL test](../../examples/README.md) is an isolated electrical
   test; disable the automatic launcher before using it.
2. Measure both Hall endpoints and the center. Confirm whether A (high Hall) or
   B (low Hall) is physically open. Check that thresholds occur before hard stops.
3. Confirm the electrical motor direction with the mechanism free and short,
   supervised movements. Do not assume the sample `A_DIRECTION` matches your wires.
4. With the actuator secured and free of the valves initially, enable the final
   program, keep hands clear and restart power. Check both requested destinations.
5. Check the PCM/scanner command and Monitor after settling. A change on GP18 is
   a commanded output; measure the line and inspect the scanner separately.
6. Validate linkage travel and operation under the actual load before relying on
   a new installation. Document any changes from the reference assembly.

## What to expect

There is no extra five-second delay. The controller retains 500 ms of startup
qualification and its input filters and reversal/start pause. The motor may move
to the PCM-requested endpoint after these intervals.

The console reports `INICIO`, `ORDEN`, `LLEGADA`, `MONITOR`, `FALLO` and
`RECUPERACION`. Messages wait until motor and brake are inactive. There are no log
files to download from the final program. Green indicates a stable close command;
red indicates a stable open command and blinks during faults. The built-in LED
stays off and BOOTSEL has no control function in the normal program.

## Faults and maintenance

After timeout, invalid Hall, lost position or a loop exception, outputs turn off.
Recovery waits 30 seconds, qualifies valid Hall plus an unchanged command for one
second, and then reinitializes the controller (including its startup filters).
Watchdog reset uses the same recovery policy. Configuration errors remain blocked.

First Ctrl+C cancels and keeps feeding the watchdog with outputs off. A second
Ctrl+C permits REPL access, but the watchdog can then reset the Pico and eventually
resume control. For maintenance, physically disconnect motor VM.

If a new build moves away from its destination, check motor direction before
increasing PWM/time. If Hall faults appear only during motion, inspect filtering,
ground routing and connections before widening validity limits. The archive
contains the development test menu, but its settings and fault policy differ from
the permanent firmware.
