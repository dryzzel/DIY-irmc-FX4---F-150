# Instalación y puesta en marcha

[Inicio](../../README.es.md) · [English](../en/installation.md)

Dirigido al Raspberry Pi Pico original RP2040 con MicroPython. El dispositivo no
requiere módulos Python externos. Las pruebas del PC usan CPython 3.11+ y no cargan
ni ejecutan código en el Pico conectado.

## Preparación

Revisar [hardware](hardware.md) y [configuración](configuration.md). Desconectar VM
del motor para copiar archivos o modificar cableado. Para programar por USB,
respetar la alimentación descrita en hardware y mantener GND común con el driver.
La versión publicada lleva `DRIVE_ENABLED=True` y puede actuar al arrancar.

Si ya hay un `/main.py` automático, detenerlo y deshabilitar ese lanzador con VM
desconectada antes de reemplazar archivos. El watchdog puede reiniciar el Pico
incluso después de Ctrl+C. Cortar/reponer alimentación con el autostart antiguo
deshabilitado antes de transferir; Stop del editor no elimina el watchdog.

Si hace falta, instalar el [firmware oficial MicroPython RPI_PICO](https://micropython.org/download/RPI_PICO/).
Respaldar primero los archivos que se quieran conservar.

## Ubicación exacta de archivos

| Archivo del repositorio | Destino en Pico |
| --- | --- |
| `pico_final/main.py` | `/main.py` |
| `pico_final/__init__.py` | `/pico_final/__init__.py` |
| `pico_final/config.py` | `/pico_final/config.py` |
| `pico_final/controller.py` | `/pico_final/controller.py` |
| `pico_final/hardware.py` | `/pico_final/hardware.py` |
| `pico_final/runtime.py` | `/pico_final/runtime.py` |

```text
Pico
├── main.py
└── pico_final/
    ├── __init__.py
    ├── config.py
    ├── controller.py
    ├── hardware.py
    └── runtime.py
```

En Thonny seleccionar MicroPython Raspberry Pi Pico y su puerto correcto. En la
vista Archivos crear `/pico_final/`, copiar los cinco módulos ahí y guardar el
lanzador como `/main.py` **al final**. El ZIP del firmware ya tiene esa estructura;
`INSTALL.txt`, `LICENSE` y `MANIFEST.json` son para el PC, no hacen falta en el Pico.

Por terminal, `python -m pip install mpremote` instala la herramienta en el PC;
`mpremote connect list` enumera puertos. Usar `connect TU_PUERTO resume` para evitar
un soft reset automático al acceder. No asumir un COM fijo ni que conectar la
herramienta deja intacto un controlador que ya esté ejecutándose.

El programa importa `pico_final.config`, no el antiguo `/config.py` suelto.
Editar en el PC, copiar al mismo directorio del Pico y reiniciar cuando esté listo.
Editar el archivo local no actualiza automáticamente la placa.

## Primera prueba en otra unidad

1. Confirmar tierra, tensiones y Monitor con VM desconectada. La
   [prueba BOOTSEL](../../examples/README.md) es aislada: antes hay que deshabilitar
   el lanzador automático.
2. Medir Hall en ambos extremos y centro. Identificar cuál extremo abre realmente:
   A es lectura alta, B lectura baja. Los umbrales deben aparecer antes del tope duro.
3. Confirmar sentido eléctrico con el mecanismo libre y movimientos cortos
   supervisados. No asumir que el signo de ejemplo coincide con otro cableado.
4. Sujetar el actuador inicialmente libre de las válvulas, habilitar el programa,
   retirar manos y reiniciar alimentación. Comprobar ambos destinos.
5. Comprobar orden y Monitor con escáner tras el asentamiento. GP18 indica una
   salida ordenada, no una medida real de voltaje; medir la línea por separado.
6. Validar recorrido de varillaje y funcionamiento con la carga real antes de
   confiar en otra instalación. Documentar diferencias con la referencia.

## Comportamiento esperado

No hay espera extra de cinco segundos. Se conservan 500 ms de validación inicial,
filtros de entrada y pausa de arranque/inversión. Después puede moverse al destino
que solicite la PCM.

Consola: `INICIO`, `ORDEN`, `LLEGADA`, `MONITOR`, `FALLO`, `RECUPERACION`.
Imprime cuando motor y freno están desactivados. El programa final no genera logs.
Verde indica cerrar; rojo abrir y parpadeo ante fallo. El LED integrado permanece
apagado; BOOTSEL no tiene función de control normal.

## Fallos y mantenimiento

Timeout, Hall inválido, posición perdida y excepción del bucle apagan las salidas.
Espera 30 s, exige un segundo de Hall válido y comando constante y reinicializa el
controlador, incluidos sus filtros de arranque. Tras watchdog aplica esa política.
Una configuración inválida permanece bloqueada.

Primer Ctrl+C cancela y alimenta el watchdog con salidas apagadas. Segundo Ctrl+C
permite REPL, pero después puede reiniciar el watchdog y reanudarse el control.
Para mantenimiento desconectar físicamente VM.

Si gira alejándose del destino, revisar dirección antes de aumentar PWM/tiempo.
Si el Hall falla solo durante movimiento, revisar filtros, retornos y conexiones
antes de ampliar límites. Las pruebas archivadas tienen ajustes y política de
fallos distintos al programa permanente.
