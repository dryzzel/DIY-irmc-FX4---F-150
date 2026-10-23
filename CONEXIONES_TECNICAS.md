# Conexiones tecnicas CMCV

Revision 2 simplificada. [Abrir diagrama SVG](CONEXIONES_TECNICAS.svg).

Referencia electrica para protoboard y placa perforada. No es un plano por agujeros. Las redes con el mismo nombre se conectan entre si; AGND y GND pertenecen a la misma red, con retornos separados de potencia.

## 1. ALIMENTACION / REDES COMUNES

```text
C1442.1 VPWR -- F1 -- [PROTECCION ENTRADA] -- VIN
                     polaridad/transitorios
                     (dimensionado pendiente)

VIN -------- LM2596 MOTOR.IN+
GND -------- LM2596 MOTOR.IN- / OUT-
LM2596 MOTOR.OUT+ -------------------------- VM
                 ajustar a 12 V bajo carga

VIN -------- LM2596 LOGICA.IN+
GND -------- LM2596 LOGICA.IN- / OUT-
LM2596 LOGICA.OUT+ ------------------------- +5V
                 ajustar a 5 V

+5V -------- D1 SS14 -------- PICO.VSYS (39)
             A ---> K
                    banda hacia VSYS
PICO.3V3 OUT (36) -------------------------- +3V3
C1442.2 / PICO.GND (38) --------------------- GND
PICO.AGND (33) ----------------------------- GND

Todos los GND son la misma red electrica.
Retorno motor/bucks directo al punto comun;
retorno analogico por AGND, sin corriente motor.
F1 y protecciones de entrada/VM no dimensionados.
No confundir +5V, +3V3 y VM.
```

## 2. PUENTE H / TB6612FNG EN PARALELO

```text
PICO.GP2 (4) -----+----- AIN1
                  +----- BIN1
PICO.GP3 (5) -----+----- AIN2
                  +----- BIN2
PICO.GP4 (6) -----+----- PWMA
                  +----- PWMB
PICO.GP5 (7) -----+----- STBY
                  |
                R1 10k
                  |
                 GND

+3V3 ------------------ VCC
VM -------------------- VM
GND ------------------- todos GND / PGND

AO1 -------------------+---------- M1
BO1 -------------------+           |
                               [ MOTOR ]
AO2 -------------------+           |
BO2 -------------------+---------- M2

C1 100nF >=50V entre M1 y M2, junto al motor.
NO unir M1 con M2; ninguno va a GND.
Unir entradas fisicamente: PWM comun.
Sin puente fijo STBY-VCC. GP27 (32) libre.
Potencia por cable soldado/bornera, no protoboard.
```

## 3. ENTRADA PCM / U1 PC817

```text
C1442.1 -- R2 10k 1/4W --+----- U1.1 A
                         |
                         K
                     D2 1N4007
                         A
                         |
C1442.3 -----------------+----- U1.2 K

PICO.GP15 (20) ---------------- U1.4 C
GND -------------------------- U1.3 E

D2 en antiparalelo al LED de U1:
  banda (K) a U1.1; anodo (A) a U1.2.
GP15 usa PULL_UP interno a 3.3 V.
No resistencia pull-up externa en este montaje.

PC817 DIP4: vista SUPERIOR, muesca arriba
                  _______
           A 1 --|   U   |-- 4 C
           K 2 --|_______|-- 3 E

U1 y U2 tienen esta misma numeracion.
Comprobar marca de pata 1 del componente real.
C1442: numeracion del diagrama del vehiculo,
NO inferir izquierda/derecha del conector.
```

## 4. MONITOR PCM / U2 PC817 + Q1

```text
PICO.GP18 (24) --+-- R3 330 -- U2.1 A
                 |
               R4 100k
                 |
GND -------------+----------- U2.2 K

+5V ------------------------- U2.4 C
U2.3 E ----- R5 3.3k ---------+---- Q1.B
                              |
                            R6 47k
                              |
GND --------------------------+---- Q1.E
C1442.4 CMCVM --------------------- Q1.C

Q1 = 2N5551 (NPN)
B = base; C = colector; E = emisor.
Confirmar orden fisico E/B/C segun fabricante.
No se asignan patas por la silueta TO-92.

GP18 alto: Q1 lleva Monitor a GND.
GP18 bajo: Monitor queda liberado.
No alimentar C1442.4 desde +5V ni +3V3.
Capacidad y niveles de esta etapa pendientes
de verificar con la carga real de la PCM.
Monitor solo tras posicion abierta confirmada.
```

## 5. HALL SS49E / SENSOR EXTERNO

```text
+3V3 -------------------------- SS49E.VCC
AGND (= GND) ------------------- SS49E.GND

SS49E.OUT -- R7 1k --+--------- PICO.GP26 (31)
                     |                 |
                   R8 100k           C2 10nF
                     |                 |
AGND ----------------+-----------------+

C3 100nF entre VCC y GND junto al SS49E.
Sensor frente a los imanes de la carcasa.
Confirmar pinout del SS49E real antes de soldar.
No conectar salida de Hall alimentado a 5V
al ADC de 3.3V.

6. DIVISOR DE TENSION VM

VM -- R9 100k 1% --+-- R11 1k --+-- GP28 (34)
                   |            |
                R10 22k 1%    C4 10nF
                   |            |
AGND --------------+------------+

VM es salida del buck motor, NO bateria.
El divisor no es proteccion de transitorios.
```

## 7. LEDs / DESACOPLO / MONTAJE

```text
GP16 (21) -- R12 1k -- LED1 VERDE A -> K -- GND
GP17 (22) -- R13 1k -- LED2 ROJO  A -> K -- GND

A = anodo; K = catodo. LEDs indican comando.

Conectar condensadores EN PARALELO a las redes:
  C5  100nF       VM    --||-- GND (driver)
  C6  470uF/25V   VM (+)--||-- GND (-)
  C7  100nF       +3V3  --||-- GND (driver)
  C8  10uF/10V    +3V3(+)||-- GND (-)
  C9  100nF       +5V   --||-- GND
  C10 100uF/10V   +5V(+) ||-- GND (-)
C1, C2, C3 y C4 estan en las secciones anteriores.
Revisar los condensadores presentes en modulos.

PROTOBOARD: solo logica/senales; potencia externa.
PERFORADA: pads aislados, puentes soldados.
Misma conectividad electrica en ambos montajes.
Cruces no conectan salvo + / punto de union.
Etiquetas iguales representan LA MISMA RED.
Numeros entre () = pin fisico del Pico original.
Los nombres del TB6612 son pines del MODULO.
No son coordenadas de agujeros ni numero del IC.

Sin sensor/corte por sobrecorriente.
PWM y timeout no limitan corriente instantanea.
```
