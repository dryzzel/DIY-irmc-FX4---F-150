# Hardware and wiring

[Home](../../README.md) · [Español](../es/hardware.md)

This is the signal-level reference for the owner's working 2007 F-150 FX4 5.4 L
3V build. It consolidates the confirmed command, Hall and Monitor connections.
It is not a complete production schematic: the exact installed input-protection
parts, fuse value, enclosure details and component brands are not fully recorded.
The successful installed operation was reported by the owner on 2026-11-27.

## Components

| Quantity | Component | Role |
| --- | --- | --- |
| 1 | Raspberry Pi Pico, RP2040 | MicroPython controller; original Pico pin numbering |
| 1 | TB6612FNG module | Bidirectional motor driver; both channels synchronized |
| 2 | Adjustable LM2596 modules | Separate nominal 12 V motor and 5 V logic supplies |
| 1 | SS49E linear Hall sensor | Measures the original two endpoint magnets |
| 2 | PC817 optocouplers | PCM command input and Monitor transistor control |
| 1 | KN2222A NPN | Pulls the PCM Monitor line to ground |
| 1 | 1N4007 | Reverse-voltage protection across the command optocoupler LED |
| 1 each | Original housing, gear train, RS-365SH motor | Reused actuator mechanics |
| 4 | 10 kΩ resistors | Command LED series, STBY pull-down, GP18 pull-down, NPN base pull-down |
| 4 | 1 kΩ resistors | Hall series filter and three in series for the NPN base |
| 1 | 620 Ω resistor | Monitor optocoupler LED series resistor |
| 1 | 10 nF ceramic (`103`) | Hall ADC filter |
| As shown below | 100 nF ceramic (`104`) | Hall supply, motor suppression, driver decoupling |
| Per supply design | Bulk capacitors and input protection | Confirm location, polarity and ratings |
| Optional | Green/red LEDs, each with 1 kΩ series resistor | Command and fault indicators |

The input resistor is documented as 10 kΩ, 1/4 W. Other resistor power ratings
must suit their circuits. Match actual component pinouts to their datasheets;
transistors or sensors with similar markings may have different pin orders.

## Vehicle connector

Use the connector's cavity numbers, not an assumed left-to-right view. Harness
and actuator faces are mirror images; identify cavities before wiring.

| C1442 cavity | Signal | Connection |
| --- | --- | --- |
| 1 | VPWR | Vehicle supply to protected module input and command input resistor |
| 2 | PWRGND | Common ground |
| 3 | CMCV | PCM command sink; command optocoupler LED cathode |
| 4 | CMCVM | Monitor input at the PCM; KN2222A collector |

For this build: PCM grounds CMCV to request closing. Released CMCV requests opening.
The command optocoupler makes GP15 low when its LED is on. A broken command wire
can look like an open request; this interface cannot distinguish the two.

## Power and ground

```text
C1442.1 -- fuse / input protection (*) --+-- LM2596 motor IN+
                                        +-- LM2596 logic IN+
C1442.2 -- common GND ----------------------+-- both IN- / OUT-
                                            +-- Pico GND
                                            +-- all TB6612 GND
                                            +-- Monitor emitter / returns

Motor buck OUT+ (nominal 12 V) ------------ TB6612 VM
Logic buck OUT+ (5 V) -------------------- Pico VSYS (physical 39)
Pico 3V3 OUT (physical 36) --------------- TB6612 VCC and SS49E VCC
```

`(*)` The exact input-protection network is not specified by this release. Do not
treat the labeled block as a wire link or assume an available RL207 and capacitor
constitute a validated automotive transient protector. Document your actual design.

The 12 V and 5 V **positive outputs do not join**. Both regulators and the Pico
share ground; the optocouplers do not make the whole system galvanically isolated.
Route motor return current to the common power ground, not through Hall AGND wiring.
Keep Pico ground connected to driver ground when testing with USB power.

With a direct buck-to-VSYS connection, physically disconnect that external 5 V
lead before powering from USB unless a suitable power-selection circuit is fitted.
Turning off the buck input is not the same as disconnecting its output. Follow the
[Pico power-supply documentation](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf)
for a combined supply design. Never connect 5 V to `3V3 OUT`.

The LM2596 is a step-down regulator; insufficient input voltage cannot produce a
regulated 12 V output. Verify VM under load and during braking. Its internal
protection does not establish a motor-current limit for this driver.
[TI LM2596 datasheet](https://www.ti.com/lit/ds/symlink/lm2596.pdf).

## Motor driver

| Pico / supply | TB6612 connection |
| --- | --- |
| GP2 | AIN1 + BIN1 |
| GP3 | AIN2 + BIN2 |
| GP4 | PWMA + PWMB |
| GP5 | STBY, with 10 kΩ to GND |
| 3.3 V | VCC |
| Motor buck | VM |
| Common ground | All GND terminals |
| Motor terminal 1 | AO1 + BO1 |
| Motor terminal 2 | AO2 + BO2 |

Read labels on the actual board: BO1/BO2 positions on this project's module differed
from an online layout. Join the matching inputs and PWM before connecting parallel
outputs. Incorrectly paired outputs can oppose each other and heat the driver.
This wiring records the working build; it does not establish a doubled continuous
or peak current rating. Both bridges share the IC's thermal limits.

Use a 100 nF ceramic capacitor rated for the application across the motor terminals,
with short leads (the development recommendation was at least 50 V). Neither motor
terminal connects directly to GND. Check local VM/GND and VCC/GND decoupling on the
module. The development notes proposed 470 µF/35 V bulk capacitance at VM; its exact
as-built location is not asserted here. It is not a transient clamp.

## Hall filter

```text
Pico 3V3 ----------------+----- SS49E VCC
                         |
                       100 nF (104), next to sensor
                         |
Pico AGND ---------------+----- SS49E GND

SS49E OUT ------ 1 kΩ ---+----- GP26 / ADC0
                         |
                        10 nF (103), next to Pico
                         |
Pico AGND ---------------+
```

AGND is Pico physical pin 33; GP26 is physical pin 31. Keep the Hall signal close
to its return, even if the motor and sensor cables must share a route. The current
filter does not include the 100 kΩ pull-down found in an older diagram.
The Hall sensor is powered at 3.3 V in this build. Do not substitute a 5 V ADC input.

## PCM command optocoupler

```text
C1442.1 VPWR -- 10 kΩ / 0.25 W -- PC817 #1 pin 1 (LED anode)
C1442.3 CMCV ------------------- PC817 #1 pin 2 (LED cathode)

1N4007 across LED: band/cathode to pin 1, anode to pin 2.
PC817 #1 pin 4 (collector) ----- GP15, internal 3.3 V pull-up
PC817 #1 pin 3 (emitter) ------- common GND
```

Do not connect the PCM's voltage directly to a Pico GPIO or pull GP15 up to 5 V.
For PC817 DIP-4, check the package's pin-1 mark: pins 1/2 are the LED and pins
4/3 are collector/emitter. Connector orientation is independent of package orientation.

## PCM Monitor stage

```text
GP18 -- 620 Ω ----------------- PC817 #2 pin 1 (LED anode)
GND --------------------------- PC817 #2 pin 2 (LED cathode)
GP18 -- 10 kΩ -- GND

Regulated +5 V ---------------- PC817 #2 pin 4 (collector)
PC817 #2 pin 3 (emitter) -- 1 kΩ -- 1 kΩ -- 1 kΩ -- KN2222A base
KN2222A base -- 10 kΩ -- GND
KN2222A emitter --------------- C1442.2 / common GND
KN2222A collector ------------- C1442.4 CMCVM
```

The PCM supplies the high level. The circuit only pulls Monitor down; do not
connect the 5 V/12 V regulator output to CMCVM. GP18=1 commands low/OPEN;
GP18=0 releases the line, with high interpreted as CLOSED. A high level during
movement or a fault is not proof that the mechanism is physically closed.
Tests reported approximately 12 V released and 0 V asserted with the PCM connected.

Identify the KN2222A base/emitter/collector for the exact part; reversing collector
and emitter caused a failed test during development. A temporary bench pull-up
must be removed before connecting the PCM. [Isolated test](../../examples/README.md).

## LEDs and unused inputs

GP16 -> 1 kΩ -> green LED anode, cathode -> GND: stable close command.
GP17 -> 1 kΩ -> red LED anode, cathode -> GND: stable open command; fault blink.
These are command indicators, not independent position measurements.
GP27 and GP28 are not used for current or VM measurement. The built-in LED stays off.

No PCB fabrication files or verified hole-by-hole perfboard layout are supplied.
The older diagrams in [the archive](../archive/README.md) are historical references.
