# Configuration reference

[Home](../../README.md) · [Español](../es/configuration.md)

The single effective configuration is [`pico_final/config.py`](../../pico_final/config.py).
Every setting has Spanish inline explanations. Values below describe `final-1`;
they are calibration from this assembly, not universal IMRC defaults.

## Endpoints and direction are independent

**A always means high Hall reading; B always means low Hall reading.**

| Setting | Meaning |
| --- | --- |
| `OPEN_END='B'` | B is open, A is closed (reference assembly) |
| `OPEN_END='A'` | A is open, B is closed |
| `A_DIRECTION=1` | IN1=1 / IN2=0 moves toward A; the opposite moves toward B |
| `A_DIRECTION=-1` | IN1=0 / IN2=1 moves toward A; the opposite moves toward B |

Changing which endpoint is open does not inherently change the electrical
direction toward A. Reversing motor wires usually requires changing the direction
sign. The old test menu's direction **2** corresponds to **-1** here, not `2`.

GP15=0 always requests closing; GP15=1 requests opening. `OPEN_END` determines
which Hall endpoint satisfies that request. Monitor uses the configured open end.

## Effective values

| Group | Values | Behavior |
| --- | --- | --- |
| Enable | `DRIVE_ENABLED=True`, `MONITOR_ENABLED=True` | Motor control and qualified Monitor enabled |
| Supply measurement | `VM_MONITOR_ENABLED=False` | No VM measurement installed; setting True is rejected |
| Motion | `MOTION_TIMEOUT_MS=3000` | Powered travel budget per stable destination |
| PWM | `PWM_START=0.40`, `PWM_RUN=0.70`, `PWM_HZ=20000` | Start/run duty and switching frequency |
| Ramp/brake | `RAMP_MS=20`, `BRAKE_MS=50` | Soft-start duration and endpoint short-brake duration |
| Pause | `REVERSE_PAUSE_MS=300` | Start/reversal/resume pause with outputs disabled |
| A endpoint | `HALL_A_ENTER=40000`, `HALL_A_EXIT=35000` | Enter at ≥40000; retain while >35000 |
| B endpoint | `HALL_B_ENTER=26000`, `HALL_B_EXIT=31300` | Enter at ≤26000; retain while <31300 |
| Hall validity | `HALL_MIN=2000`, `HALL_MAX=63500` | Raw samples must be strictly inside both bounds |
| Filters | `HALL_STABLE_MS=30`, `COMMAND_STABLE_MS=50` | Stable classification/command qualification |
| Startup/settle | `STARTUP_MS=500`, `SETTLE_MS=150` | Initial qualification and settled arrival |
| Sampling | `HALL_SAMPLES=8`, `LOOP_MS=1` | Average eight reads; sleep 1 ms between iterations |
| Recovery | `RECOVERY_WAIT_MS=30000`, `RECOVERY_VALID_MS=1000` | Fault wait, then continuous input qualification |
| Watchdog | `WATCHDOG_MS=1000` | Reset if the loop fails to feed it |
| Indicators/console | `FAULT_BLINK_MS=250`, `CONSOLE_PENDING=16` | Fault LED half-period; bounded event queue |

ADC values are `read_u16()` counts, not voltage or angular position. Classification
uses hysteresis so small motion/noise does not immediately lose an endpoint.
The average is used for position; **any** raw sample outside the valid range faults.
`LOOP_MS` is a sleep, not a guaranteed sampling period.

Changing thresholds must preserve:

```text
HALL_MIN < HALL_B_ENTER < HALL_B_EXIT < HALL_A_EXIT < HALL_A_ENTER < HALL_MAX
```

`DRIVE_ENABLED=False` produces diagnostic behavior with motor and Monitor off.
`MONITOR_ENABLED=False` leaves the Monitor transistor off/released. These are
software settings, not a substitute for removing motor power while rewiring.

## Timeout and recovery

Opening for 1.5 seconds and then receiving a confirmed close command gives closing
its own three-second budget. Brief input glitches do not reset that budget.
Pauses and braking do not consume powered travel time. Settled arrival resets it.

After a fault or watchdog reset, motor and Monitor turn off. Recovery has no retry
limit: after the wait and input qualification, a new controller follows the current
PCM request. This is not jam detection or current protection. Configuration errors
remain blocked instead of retrying.

## Pin assignments

`PIN_*` values are **GPIO numbers**, not physical connector pin numbers:

| Setting | GPIO | Function |
| --- | --- | --- |
| `PIN_STBY` | 5 | Driver enable |
| `PIN_MONITOR` | 18 | Monitor optocoupler output |
| `PIN_IN1`, `PIN_IN2` | 2, 3 | Driver direction |
| `PIN_PWM` | 4 | Both driver PWM inputs |
| `PIN_COMMAND` | 15 | Command optocoupler input with internal pull-up |
| `PIN_HALL` | 26 | ADC0 Hall input |
| `PIN_GREEN`, `PIN_RED` | 16, 17 | External LEDs |

The validator requires this pin map because the launcher's emergency disable
uses fixed GP5 and GP18. Changing only these constants is not a supported pin-remap
procedure. The built-in LED is deliberately off; BOOTSEL is unused by the final code.
