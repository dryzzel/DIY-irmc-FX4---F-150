# Referencia de configuración

[Inicio](../../README.es.md) · [English](../en/configuration.md)

La configuración efectiva está en [`pico_final/config.py`](../../pico_final/config.py),
con comentarios en español para cada ajuste. Los valores de `final-1` pertenecen
a este montaje; no son una calibración universal para cualquier IMRC.

## Extremos y sentido son independientes

**A siempre representa Hall alto; B siempre representa Hall bajo.**

| Ajuste | Significado |
| --- | --- |
| `OPEN_END='B'` | B abierto, A cerrado (montaje de referencia) |
| `OPEN_END='A'` | A abierto, B cerrado |
| `A_DIRECTION=1` | IN1=1 / IN2=0 mueve hacia A; contrario hacia B |
| `A_DIRECTION=-1` | IN1=0 / IN2=1 mueve hacia A; contrario hacia B |

Cambiar cuál extremo abre no obliga a cambiar el sentido eléctrico hacia A.
Si se invierten los cables del motor, normalmente se cambia el signo de dirección.
El sentido **2** del menú antiguo equivale a **-1** aquí: no se admite `2`.

GP15=0 siempre solicita cerrar y GP15=1 abrir. `OPEN_END` determina el destino
Hall correspondiente y el extremo que permite activar Monitor.

## Valores efectivos

| Grupo | Valores | Comportamiento |
| --- | --- | --- |
| Habilitación | `DRIVE_ENABLED=True`, `MONITOR_ENABLED=True` | Movimiento y Monitor condicionado activos |
| Medición VM | `VM_MONITOR_ENABLED=False` | No instalada; True es rechazado |
| Movimiento | `MOTION_TIMEOUT_MS=3000` | Marcha por destino estable |
| PWM | `PWM_START=0.40`, `PWM_RUN=0.70`, `PWM_HZ=20000` | Activación inicial/final y frecuencia |
| Rampa/freno | `RAMP_MS=20`, `BRAKE_MS=50` | Arranque gradual y frenado al llegar |
| Pausa | `REVERSE_PAUSE_MS=300` | Espera antes de arrancar/invertir/reanudar |
| Extremo A | `HALL_A_ENTER=40000`, `HALL_A_EXIT=35000` | Entrada ≥40000; retención >35000 |
| Extremo B | `HALL_B_ENTER=26000`, `HALL_B_EXIT=31300` | Entrada ≤26000; retención <31300 |
| Hall válido | `HALL_MIN=2000`, `HALL_MAX=63500` | Muestras crudas estrictamente entre límites |
| Filtros | `HALL_STABLE_MS=30`, `COMMAND_STABLE_MS=50` | Clasificación Hall y comando estables |
| Inicio/asentamiento | `STARTUP_MS=500`, `SETTLE_MS=150` | Validación inicial y llegada asentada |
| Muestreo | `HALL_SAMPLES=8`, `LOOP_MS=1` | Promedio de ocho lecturas y espera de 1 ms |
| Recuperación | `RECOVERY_WAIT_MS=30000`, `RECOVERY_VALID_MS=1000` | Espera y validación continua posterior |
| Watchdog | `WATCHDOG_MS=1000` | Reinicia si el bucle deja de alimentarlo |
| Indicador/consola | `FAULT_BLINK_MS=250`, `CONSOLE_PENDING=16` | Medio ciclo del LED y cola acotada |

Hall usa cuentas `read_u16()`, no voltios ni grados. La histéresis tolera pequeñas
variaciones sin perder enseguida el extremo. Se usa la media para posición, pero
**cualquier** muestra cruda fuera de rango causa fallo. `LOOP_MS` es una espera,
no una garantía de periodo exacto de lectura.

Debe conservarse este orden al modificar umbrales:

```text
HALL_MIN < HALL_B_ENTER < HALL_B_EXIT < HALL_A_EXIT < HALL_A_ENTER < HALL_MAX
```

`DRIVE_ENABLED=False` deja motor y Monitor apagados en diagnóstico.
`MONITOR_ENABLED=False` deja el transistor Monitor desactivado y la línea libre.
Estos ajustes no sustituyen desconectar VM para modificar cableado.

## Timeout y recuperación

Si abre 1,5 s y después confirma una orden de cerrar, cerrar dispone de sus propios
3 s. Ruido breve no renueva el contador. Pausa y freno no consumen tiempo de marcha.
Una llegada asentada también lo reinicia.

Fallo o watchdog apagan motor y Monitor. No hay límite de reintentos: tras la
espera y validación se crea un controlador que sigue la orden vigente de la PCM.
No es detección de atasco ni protección de corriente. Configuración inválida
permanece bloqueada sin reintentar.

## Pines

Los valores `PIN_*` son **números GPIO**, no patillas físicas:

| Ajuste | GPIO | Función |
| --- | --- | --- |
| `PIN_STBY` | 5 | Habilitación del driver |
| `PIN_MONITOR` | 18 | Opto Monitor |
| `PIN_IN1`, `PIN_IN2` | 2, 3 | Sentido de giro |
| `PIN_PWM` | 4 | PWM de ambos canales |
| `PIN_COMMAND` | 15 | Entrada del opto con pull-up interno |
| `PIN_HALL` | 26 | ADC0 Hall |
| `PIN_GREEN`, `PIN_RED` | 16, 17 | LED externos |

El validador exige este mapa porque el apagado de emergencia del lanzador usa
GP5 y GP18 fijos. Cambiar solo las constantes no permite reasignar el cableado.
LED integrado apagado y BOOTSEL sin función en el programa final.
