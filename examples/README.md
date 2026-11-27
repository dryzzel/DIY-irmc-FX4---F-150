# Isolated Monitor test / Prueba aislada del Monitor

[`monitor_bootsel.py`](monitor_bootsel.py) is the original manual electrical test.
With the automatic program disabled, each debounced BOOTSEL press toggles GP18.
The built-in LED indicates the commanded transistor state, not measured PCM
voltage or actuator position. STBY remains low; the motor is not driven.

Before using it, remove motor VM, disable the existing `/main.py` autostart, and
power-cycle to clear any running watchdog. Run the example from the editor/REPL,
not alongside the permanent controller. The PCM or a temporary bench pull-up
provides the Monitor's high voltage; never feed an external pull-up into the PCM.
Measure the actual output with a meter. Restore the final launcher afterwards.

## Español

Esta prueba conmuta el Monitor con BOOTSEL y mantiene STBY apagado. Antes de usarla,
quita VM, deshabilita el `main.py` automático y reinicia la alimentación para
limpiar su watchdog. El LED indica GP18, no la posición ni el voltaje medido.
La PCM aporta el nivel alto; el transistor solo lleva la línea a tierra.
Después restaura el lanzador final. Esta prueba no forma parte del arranque normal.
