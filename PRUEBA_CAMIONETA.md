# Prueba automatica temporal: actuador libre, conector de la camioneta

El usuario confirma motor y engranajes en la carcasa, SIN conectar la salida a las valvulas, y alimentacion desde el conector C1442. No es una prueba con carga real ni un controlador final para circular.

## Archivos que debes copiar con Thonny

La carpeta `pico_prueba_camioneta` contiene los cinco archivos preparados. Copia su CONTENIDO a la raiz del Pico, no la carpeta:

- `main.py`: lanzador temporal de esta prueba.
- `prueba_camioneta.py`: automatico y registro.
- `prueba_tb6612.py`: conexiones, valores y funciones probadas; al importarlo no abre el menu.
- `controller.py`: maquina de estados.
- `config.py`: valores base, modificados solo en memoria para esta prueba.

El `main.py` original de la carpeta del proyecto NO se modifica. Guarda una copia del que tengas en el Pico antes de sustituirlo. No necesitas copiar tests ni archivos JSON anteriores.

En Thonny: Ver > Archivos, seleccionar interprete MicroPython (Raspberry Pi Pico), abrir la carpeta local y subir los cinco archivos a Raspberry Pi Pico. Alternativamente, abrir cada archivo y Archivo > Guardar como > Raspberry Pi Pico con su nombre exacto. Para detener el arranque automatico, con VM desconectada, usa Stop y renombra/elimina el main.py temporal del Pico.

Mientras programes por USB, desconecta fisicamente el cable de 5 V externo de VSYS. Al terminar, desconecta USB y restituye ese cable con todo apagado. Mantener GND comun.

## Valores de esta version

| Parametro | Valor |
|---|---|
| GP15=0 / PC817 encendido | A cerrado, sentido 1 |
| GP15=1 / PC817 apagado | B abierto, sentido 2 |
| A / B entrada | 40000 / 26000 |
| Retencion A / B | 35000 / 31300 |
| PWM inicial / final | 25 % / 60 % |
| Rampa de arranque | 20 ms |
| Freno | 50 ms, luego rueda libre |
| Timeout de marcha acumulada | 3000 ms |
| Espera inicial | 5 segundos, luego estabilizacion del controlador |
| Duracion maxima | 10 minutos desde fin de espera inicial |
| Monitor y lectura VM | Deshabilitados |

Se toma DIRECCION_A=1 del archivo actual, tras invertir los cables al soldar. Si la copia que probaste en el Pico tiene otros valores, compara antes de reemplazarla. No se aumenta potencia ni timeout automaticamente.

## Conexion de la prueba al ramal

Con alimentacion quitada y numeracion del diagrama del vehiculo verificada (no deducir izquierda/derecha):

```text
C1442 pin 1 VPWR ---- alimentacion de entrada de ambos LM2596
                 +-- resistencia 10k -- PC817 pata 1
C1442 pin 2 GND ----- punto comun de tierras
C1442 pin 3 CMCV ---- PC817 pata 2
C1442 pin 4 CMCVM --- SIN CONECTAR; aislar

PC817 pata 4 -------- Pico GP15 (fisico 20)
PC817 pata 3 -------- GND Pico
LM motor OUT+ ------- VM TB6612
LM logica OUT+ ------ VSYS Pico (fisico 39), SIN USB conectado
Ambos OUT- ---------- GND comun, junto con GND Pico y driver
```

Conservar diodo antiparalelo del PC817 y filtros Hall/motor del esquema de cableado. No conectar pin 3 directamente a GP15. No conectar pin 4 a tierra ni generar confirmacion falsa.

**Limite electrico pendiente:** el ramal del vehiculo puede presentar transitorios. Este diagrama identifica las conexiones pero no completa la proteccion de entrada ya pendiente en CONEXIONES_TECNICAS.md. RL207 y 470uF no sustituyen una proteccion de sobretension; el programa tampoco. El LM2596 no eleva tension durante caidas de alimentacion y no se mide VM en esta prueba. No se certifica la alimentacion directa del vehiculo como protegida.

## Secuencia

1. Verificar primero en banco el arranque sin Thonny y la creacion de un archivo de registro. Mantener actuador libre, fijado y sin manos cerca de salida/engranajes.
2. Quitar alimentacion, retirar USB y conectar al ramal con el contacto apagado. No cambiar soldaduras o puentes con tension. Confirmar previamente que ambos bucks siguen ajustados y que 5 V/12 V no estan unidos.
3. Primera prueba con la camioneta estacionada, freno de estacionamiento y actuador sujeto, SIN carga de las valvulas. Al recibir alimentacion, los dos LED parpadean durante 5 segundos; luego puede moverse inmediatamente segun la entrada PCM.
4. Si el comando cambia, ejecuta el movimiento. No genera ordenes PCM ni garantiza que la PCM abra acelerando en vacio. No usar esta prueba como motivo para salir a conducir.
5. Si no hay cambios de comando, dejalo unos segundos: el registro permite ver GP15 y la posicion. No aumenta PWM ni reintenta un fallo por cambiar la entrada.
6. Tras la ultima parada, espera al menos 3 segundos antes de retirar alimentacion para permitir guardar datos. Desconecta primero el ramal, y para leer por USB desconecta los 5 V externos de VSYS.
7. Descarga `logs_cmcv/prueba_01.jsonl` (o el numero mas reciente) con el panel Archivos de Thonny y compartelo completo.

## Indicadores

- Ambos parpadeando: espera inicial.
- Verde: comando estable GP15=0 (cerrar).
- Rojo: comando estable GP15=1 (abrir).
- Ambos apagados brevemente: comando en estabilizacion.
- Rojo parpadeando: prueba detenida por fallo, limite de tiempo o cancelacion. Consultar evento FIN; no equivale necesariamente a averia.

Los LED indican comando, no confirman por si solos posicion. Un fallo real de registro o agotamiento de los ocho archivos detiene movimiento; llenar un fragmento individual ya no lo detiene.

## Archivos y datos

Revision 2: cada arranque reserva un archivo distinto: `logs_cmcv/prueba_01.jsonl` a `prueba_08.jsonl`. No se borran ni sobrescriben archivos anteriores. Maximo 128 KiB por archivo, con 1 KiB reservado para el evento FIN. Al llenarse un fragmento, continua en el siguiente archivo libre con evento CONTINUACION y referencia al anterior; compartir todos los fragmentos. Si se ocupan los ocho archivos, detiene el motor y guarda FIN con REGISTROS_LLENO, indicando cuantos eventos pendientes no pudo guardar. Descargar y borrar manualmente los registros antes de otra prueba; no se borran automaticamente.

Cada linea es un objeto JSON independiente, no un unico JSON con todo el ensayo:

- INICIO: causa de reinicio y configuracion efectiva.
- ESTADO: milisegundos desde el fin de espera inicial, GP15 crudo/estable, destino, Hall, min/max crudos desde el registro previo, intervalo maximo Hall con potencia activa, direccion, PWM, freno, posicion y fallo.
- FIN: motivo de parada. FIN_TIEMPO significa que termino la ventana de 10 minutos; no es un timeout de movimiento.

Los estados se acumulan en RAM (maximo 256) durante marcha/frenado. Se muestrea para el registro cada 50 ms durante movimiento y asentamiento, cada 5 s en reposo y cuando cambia el estado/comando. El control sigue leyendo cada ~1 ms mas el tiempo de ejecucion; ese intervalo no esta garantizado.

Revision 3: se escribe flash SOLO con STBY apagado, sin freno activo. El guardado normal ocurre en DETENIDO despues de 800 ms. Si se acumulan 64 registros, se permite guardar en INICIO, PAUSA, ASENTANDO o DETENIDO tras al menos 50 ms sin potencia, para que los cambios frecuentes de comando no llenen el buffer. Tambien guarda despues de apagar por fallo/fin. Durante esa escritura no se lee la PCM; cualquier cambio se detecta en la siguiente vuelta. El buffer lleno provoca parada, no perdida silenciosa de datos.

No se garantiza conservar el ultimo tramo ante corte brusco de alimentacion: la RAM se pierde y una escritura puede quedar incompleta. Las lineas completas anteriores son las recuperables. Ausencia de FIN significa finalizacion no registrada, no exito.

Durante la escritura, solo con STBY=0, se alimenta el watchdog entre lineas y operaciones de guardado. Una operacion individual que se bloquee mas de un segundo todavia puede provocar un reinicio.

Watchdog de 1 segundo: si el programa se bloquea, reinicia. Un arranque identificado como RESET_WATCHDOG queda sin movimiento, no reintenta. No es un limitador de corriente ni un freno inmediato. Revisar el registro antes de reiniciar; desconectar/reconectar alimentacion inicia una nueva prueba. Tras finalizar, el programa mantiene potencia apagada y alimenta el watchdog; Ctrl+C vuelve al editor pero el watchdog sigue activo y puede reiniciar despues. Para recuperar archivos trabajar con VM desconectada.

No existe supervision de corriente, ni proteccion de atasco por hardware, ni Monitor. Un codigo PCM por Monitor ausente no demuestra fallo del movimiento.

## Validacion local

Tests simulados verifican ambas direcciones y freno, que no se escribe con STBY habilitado, parada por saturacion Hall, timeout bloqueado, fallo de escritura y bloqueo tras reinicio watchdog. No sustituyen la prueba en Pico ni validan potencia/temperatura/transitorios.

Referencia: [MicroPython WDT](https://docs.micropython.org/en/latest/library/machine.WDT.html).

Revision 2 corrige la parada por limite de archivo observada en prueba_08.jsonl (130902 bytes, siguiente linea excedia 131072). Los archivos 06 y 07 solo registran bloqueo de arranque por watchdog; no prueban por si solos que la escritura originara esos reinicios. El watchdog y los limites del motor se conservan.

Revision 3: corregido BUFFER_LLENO observado a los 20462 ms. Una simulacion con cambios de comando cada 1100 ms reprodujo el fallo anterior; ahora guarda durante las pausas sin habilitar escritura con el driver activo. Se mantienen los limites de motor y el watchdog.

Revision 4: habilita tambien el guardado preventivo durante INICIO, con STBY=0, sin freno y al menos 50 ms sin potencia. La version 3 podia llenar el buffer si GP15 cambiaba continuamente antes de estabilizarse. Caso reproducido con entrada que alterna cada 2 ms; el controlador no habilita movimiento y conserva esos cambios en los registros. Esto no confirma la causa de una parada real sin leer su version y las lineas anteriores al fallo.
