> **ARCHIVED / ARCHIVADO:** Earlier revision; not current installation guidance.
> Use [current hardware](../en/hardware.md) / [hardware actual](../es/hardware.md).
> Historical scripts are now in [legacy](../../legacy/README.md).

# CMCV — Pico, TB6612FNG en paralelo y SS49E

Revision de construccion 2, simplificada. Firmware completo para calibracion y pruebas.
NO es una instalacion automotriz validada. Motor y Monitor salen deshabilitados
en config.py hasta medir direccion, extremos y tiempo de recorrido.
Los dos LM2596 se conservan; el del motor no tiene limitacion ajustable confirmada.

Vista general imprimible: [ESQUEMA_FINAL.svg](ESQUEMA_FINAL.svg).
Diagrama tecnico por redes y terminales: [CONEXIONES_TECNICAS.svg](CONEXIONES_TECNICAS.svg).
Version de texto: [CONEXIONES_TECNICAS.md](CONEXIONES_TECNICAS.md).
Las tablas y conexiones de este documento definen el cableado; la vista general
no reemplaza el detalle ni representa una PCB lista para fabricar.

## Lo medido y lo pendiente

- C1442: 1 VPWR, 2 PWRGND, 3 CMCV, 4 CMCVM, segun diagrama del usuario.
- Entrada PC817 probada: 12-14 V entre 1 y 3 en un estado, 1.6 V en el otro.
  Los LEDs estaban intercambiados; verde correcto en GP16, rojo en GP17.
- La interpretacion provisional es opto ON/GP15 LOW = cerrar; OFF/HIGH = abrir.
- Hall SS49E, imanes N/S, A ~38600, B ~26600. Falta determinar cual es abierto.
- Stall confirmado por el usuario: eje sujeto mientras seguia alimentado y al
  conectar la bateria. Maximo indicado 2.5 A una vez durante menos de un segundo;
  otras pruebas 1.6-1.9 A. Estas lecturas no capturan necesariamente el pico real.
- En giro reporto 0.3-0.4 A y ocasionalmente 0 A; revisar esa lectura y confirmar
  consumo/tiempo con la carga mecanica instalada.
- Faltan direccion, tiempo con carga, retencion mecanica, carga/tensiones del
  Monitor y comportamiento termico dentro de la carcasa.
- La apertura de un cable de comando es indistinguible de una orden de abrir
  con esta entrada. Supervisar VM no elimina esa ambiguedad.

## 1. Alimentacion y tierras

```text
C1442-1 VPWR -- F1 -- proteccion polaridad/transitorios -- VPWR_PROTEGIDA
                                                         |
                    +------------------------------------+----------------+
                    |                                                     |
              LM2596 MOTOR                                          LM2596 LOGICA
             ajustar a 12 V                                        ajustar a 5 V
                    |                                                     |
                    |                                              +5V_LOGICA
                    |                                                     |
                    |                                         Schottky SS14
                    |                                         anodo -> catodo
                   VM                                             (banda)
                    |                                                     |
              TB6612 VM                                       VSYS Pico (39)

C1442-2 PWRGND ------ PUNTO DE TIERRA COMUN
                     |    |    |     |      |
                   buck buck driver Pico  sensores/Monitor
```

Los LM2596 NO son aislados. El diseño completo tiene tierra comun aunque use optos.
Conectar los retornos del motor y reguladores directamente al punto comun;
no pasar corriente del motor por el cable de AGND o por la placa Pico.
Motor entre salidas del puente, nunca con un terminal permanentemente a tierra.

5 V solo a VSYS por SS14; NO al pin 3V3. El diodo evita retorno de USB al buck.
VCC del TB6612 y SS49E reciben 3V3 OUT (36) del Pico.
No alimentar desde el USB de la camioneta ni PC a red durante las pruebas del ramal.
La proteccion de VSYS contra retorno no aisla la tierra del USB.

Componentes de desacoplo iniciales (revisar los ya presentes en los modulos):

- VM, junto al driver: 100 nF ceramico + 470 uF/25 V, positivo a VM.
- VCC del driver: 100 nF + 10 uF/10 V hacia GND.
- +5V_LOGICA: 100 nF + 100 uF/10 V hacia GND.
- SS49E: 100 nF entre alimentacion y GND junto al componente.
- Motor: 100 nF ceramico >=50 V entre bornes; cables cortos/trenzados.
- No colocar un diodo rectificador simple en paralelo al motor bidireccional.

F1 se dimensiona segun consumo medido y cableado, no por el numero impreso en el buck.
Para banco usar fuente con limitacion de corriente. Para vehiculo, el bloque de
entrada requiere fusible, proteccion de polaridad y supresion de transitorios
dimensionados como conjunto: no se ha elegido un TVS solo por su tension nominal.
No sustituir ese bloque por un puente para instalar permanentemente.

El LM2596 no eleva tension: no entrega 12 V regulados si la entrada es insuficiente.
Verificar salida bajo carga antes de conectar el driver. VM debe mantenerse dentro
del rango del TB6612, incluso al frenar/regenerar. El buck no absorbe necesariamente
energia regenerada; el condensador no garantiza por si solo limitar la sobretension.
La proteccion final de VM y de entrada queda pendiente de medir transitorios.

### Version sin medicion ni corte de corriente

Se eliminan shunt, INA180/ACS712/INA219, LM393 y cualquier circuito adicional de
corte por sobrecorriente. La salida del LM2596 del motor va directamente a VM.
GP27 queda libre. No se requiere verificar un limitador para habilitar el firmware.

Se conservan Hall, arranque progresivo, techo de PWM, timeout con fallo bloqueado,
pausa de inversion, vigilancia de VM y watchdog. No hay reintento automatico tras
un fallo. Si se atasca sin alcanzar el extremo, el timeout detiene el motor;
el programa no puede reconocer sobrecorriente ni cortar por amperaje.

PWM y timeout no limitan la corriente instantanea ni garantizan que el TB6612
sobreviva a un bloqueo. La limitacion interna del LM2596 no esta ajustada para
proteger este driver. No asumir 6.4 A sumando picos: los canales comparten chip y
limites termicos. Se mantienen fusible y protecciones de entrada/VM.

## 2. TB6612FNG: unir ambos canales fisicamente

| Conexion | Destino |
|---|---|
| GP2, fisico 4 | AIN1 y BIN1 unidos |
| GP3, fisico 5 | AIN2 y BIN2 unidos |
| GP4, fisico 6 | PWMA y PWMB unidos |
| GP5, fisico 7 | STBY; agregar 10 kohm STBY-GND |
| 3V3 OUT, fisico 36 | VCC |
| VM | Salida del LM2596 del motor, ajustada a 12 V |
| GND/PGND | Tierra comun |
| AO1 + BO1 | Terminal M1 del motor |
| AO2 + BO2 | Terminal M2 del motor |

Usar nombres de red, no posicion fisica del modulo. Todos los pines VM/GND
del chip deben estar conectados; las placas normalmente ya los agrupan.
NO unir AO1 con AO2. No usar dos PWM distintos ni duplicar señales por software.
STBY debe estar libre de un puente fijo a VCC; verificar el modulo.

```text
 GP2 ---+-- AIN1                  AO1 --+
        +-- BIN1                  BO1 --+--- M1
 GP3 ---+-- AIN2                              MOTOR
        +-- BIN2                  AO2 --+--- M2
 GP4 ---+-- PWMA                  BO2 --+
        +-- PWMB
 GP5 ------ STBY ---[10k]--- GND
```

Se usa STBY=0 para detener en alta impedancia (rueda libre). No freno activo ni
corriente permanente de mantenimiento. Confirmar que el mecanismo conserva la
posicion; si retrocede, el firmware bloquea POSICION_PERDIDA, no insiste indefinidamente.

## 3. Entrada PCM: PC817 numero 1

```text
C1442-1 --[10k, 1/4 W]-- PC817 #1 pata 1 (anodo)
C1442-3 ---------------- PC817 #1 pata 2 (catodo)
GP15 (fisico 20) -------- PC817 #1 pata 4 (colector)
GND -------------------- PC817 #1 pata 3 (emisor)
```

1N4148 o 1N4007 antiparalelo entre patas 1 y 2: banda a 1, anodo a 2.
El GPIO usa Pin.PULL_UP interno. No agregar 47k externa ni conectar 12 V al GPIO.
Se conserva la rama de 10k probada. A ~1.2 mA de LED, no queda garantizado el CTR
minimo publicado a 5 mA: repetir niveles con temperatura/alimentacion antes de instalar.
La alimentacion de esta rama es VPWR del conector, no la salida de 5 V.

## 4. SS49E y ADC

| Señal SS49E | Conexion |
|---|---|
| VCC | 3V3 OUT (36) |
| GND | AGND (33), unido a tierra comun con retorno de señal |
| OUT | Por 1 kohm a GP26/ADC0 (31) |

En GP26 colocar 10 nF y 100 kohm a AGND. El pull-down permite detectar un cable
de salida abierto como lectura baja; no detecta todos los fallos plausibles del sensor.
No alimentar el Hall a 5 V con salida directa al ADC. Comprobar patas del encapsulado
SS49E exacto en su hoja de datos. Recalibrar tras filtros, montaje y alimentacion final.

## 5. Supervision de VM

Se conserva el divisor de tension para GP28; GP27/ADC1 (32) queda sin conectar.

```text
VM --[100k, 1%]--+--[1k]-- GP28/ADC2 (34)
                |              |
             [22k, 1%]       [10nF]
                |              |
               AGND           AGND
```

Todas las entradas ADC deben quedar dentro de 0..3.3 V. El divisor mide tension;
no limita corriente ni protege contra transitorios. Presupone VM dentro de limites,
no conectarlo directamente a bateria. Evitar tension externa en los ADC con Pico
apagado. Verificar la lectura contra el multimetro antes de habilitar movimiento.

## 6. Salida Monitor: PC817 numero 2 + transistor

Se propone colector abierto, no una resistencia artificial de 60 ohm.
Capacidad objetivo inicial <=10 mA, pendiente de caracterizar la PCM.

```text
GP18 (fisico 24) --[330 ohm]-- PC817 #2 pata 1
GND ------------------------- PC817 #2 pata 2
GP18 --[100k]-- GND

+5V_LOGICA ------------------- PC817 #2 pata 4 (colector)
PC817 #2 pata 3 (emisor) --[3.3k]-- BASE Q1 (2N5551)
                                      |
                                    [47k]
                                      |
GND ----------------------------- EMISOR Q1
C1442-4 CMCVM ------------------- COLECTOR Q1
```

Comprobar el pinout E/B/C de Q1 segun fabricante; no asumir orden por encapsulado.
GP18 HIGH enciende opto y Q1, llevando Monitor a tierra; LOW libera.
No conectar Monitor a +5 V, 3V3 ni GPIO. No poner resistencia de 14k por suposicion.
El segundo opto no hace aislado al sistema porque las tierras ya estan unidas.

Antes de conectar C1442-4, probar con una fuente de banco de 12 V y resistencia
de 2.2k desde +12 V al colector (carga ~5.5 mA), luego medir nivel alto/bajo.
Para hacerlo sin mover motor, desconectar potencia y usar manualmente GP18 desde REPL
con el programa detenido. Confirmar que arranque, reset y falta de 5 V dejan Q1 apagado.
En PCM, primero caracterizar el pin 4 mediante una carga limitada conocida y medir
tension sobre esa carga para calcular corriente. No usar amperimetro directo a tierra.
No habilitar MONITOR_ENABLED hasta comprobar corriente <= capacidad de esta etapa
y niveles aceptados por PCM. Si requiere mas corriente, redimensionar la etapa.

El software libera Monitor al cerrar, durante movimiento, fallo o señal inestable.
Solo lo activa tras extremo abierto confirmado y asentado. Una lectura inestable
del Hall o del comando reinicia el tiempo de asentamiento: no reutiliza la
confirmacion anterior al desaparecer el ruido. No detecta transistor
de Monitor en corto ni verifica lo que realmente lee la PCM: validar con escaner.

## 7. LEDs

GP16 (21) -- 1k -- anodo verde; catodo a GND.
GP17 (22) -- 1k -- anodo rojo; catodo a GND.
Verde = comando LOW, rojo = HIGH. Rojo intermitente = fallo bloqueado.
LEDs indican comando, no posicion. No repetir el intercambio GP16/GP17.

## 8. Firmware y calibracion

Copiar al Pico `main.py`, `controller.py` y `config.py` en la raiz.
`prueba_entrada.py` conserva la prueba anterior; no se necesita para el controlador.
`test_controller.py` y `test_runtime.py` se ejecutan solo en PC, no se copian al Pico.

Arranque predeterminado: DIAGNOSTICO, STBY=0, Monitor liberado, LEDs y lecturas
activas. Puede comprobarse Hall sin motor. Montar y verificar Hall y divisor VM
antes de habilitar movimiento; no se utiliza ningun sensor de corriente.

1. Con mecanica desacoplada donde corresponda, identificar posiciones sin forzar
   engranajes/topes. Registrar cual es ABIERTO y guardar OPEN_END='A' o 'B'.
2. Con fuente limitada y pulsos cortos controlados de banco, determinar direccion
   de M1/M2: A_DIRECTION=1 si IN1=1/IN2=0 mueve a A; -1 si es al contrario.
   El firmware normal no incluye un modo de forzar movimiento que omita protecciones.
3. Medir corriente de arranque/recorrido, tiempo y capacidad de retencion. Fuente
   y medidor deben poder captar picos; un promedio de multimetro no los certifica.
4. Ajustar MOTION_TIMEOUT_MS segun recorrido real con un margen pequeno.
   No usar automaticamente los 10 segundos del codigo antiguo.
5. Validar divisor VM y Hall. Ajustar PWM_RUN y RAMP_MS en banco; no asumir
   que 50% garantiza par ni que PWM limita corriente de bloqueo.
6. DRIVE_ENABLED=True habilita el control una vez configurado. Probar primero
   comandos simulados sin PCM y Monitor desconectado.
7. Probar arranque en A/B/medio, cambios durante movimiento, ruido, sensor abierto,
   caida de alimentacion y reinicio. Simular timeout con motor desconectado y
   Hall entre extremos, sin bloquear fisicamente el motor para esta prueba.
8. Validar la etapa Monitor y despues MONITOR_ENABLED=True.

El watchdog de 500 ms reinicia ante bloqueo del programa. El arranque detecta un
reset de watchdog y mantiene fallo; requiere corte de alimentacion tras resolver
la causa. Resistencias STBY-GND y GP18-GND mantienen salidas apagadas durante reset.
Un fallo persiste aunque cambie el comando. No hay reintento automatico en esa sesion.
Un corte total y nuevo encendido elimina el fallo en RAM: inspeccionar antes de reiniciar.

## 9. Verificacion y limites de entrega

Ejecutar en PC: `python -m unittest -v test_controller test_runtime`.
Resultado local de esta revision: 19 pruebas aprobadas. Incluyen ejecucion de
main.py con perifericos simulados, apagado ante excepciones y bloqueo tras watchdog.
Las pruebas simulan la maquina de estados y el adaptador, no electromecanica, MicroPython real,
capacidad de corriente, temporizacion real, carga Monitor ni transitorios.
Codigo/esquema no equivalen a un reemplazo homologado o validado en la camioneta.
No instalar permanentemente hasta completar los parametros y la proteccion de entrada/VM.

## Fuentes

- Toshiba TB6612: https://toshiba.semicon-storage.com/info/datasheet_en_20141001.pdf?did=10660
- Conexion paralela, soporte Pololu: https://forum.pololu.com/t/tb6612fng-dual-motor-driver-paralleled/1750
- TI LM2596: https://www.ti.com/lit/ds/symlink/lm2596.pdf
- Sharp PC817: https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf
- onsemi 2N5551: https://www.onsemi.com/pdf/datasheet/2n5551t-d.pdf
- Pico alimentacion: https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf
- Honeywell SS49E: https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/en-us/products/sensors/magnetic-sensors/linear-and-angle-sensor-ics/common/documents/sps-siot-ss39et-ss49e-ss59et-product-sheet-005850-3-en-ciid-50359.pdf
