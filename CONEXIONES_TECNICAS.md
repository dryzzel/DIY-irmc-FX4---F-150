# Cableado permanente sin PCB ? revision 3

[Abrir diagrama tecnico actualizado (SVG)](CABLEADO_SIN_PCB.svg).

Montaje punto a punto con los modulos existentes, basado en las pruebas de banco. Motor y engranajes probados; carga real de valvulas y proteccion de alimentacion del vehiculo pendientes. Monitor omitido por decision del usuario.

**Este documento sustituye el cableado de la revision 2.** Los antiguos CONEXIONES_TECNICAS.svg/.png/.pdf y ESQUEMA_FINAL son referencias anteriores, no el plano de esta revision.

## 1. ALIMENTACION: DOS LM2596 EN PARALELO POR LA ENTRADA

```text
Fuente de banco / VIN protegido ----+---- LM MOTOR IN+
                                   +---- LM LOGICA IN+
GND COMUN -------------------------+---- ambos IN-

LM MOTOR OUT+ (ajustado a 12 V) ---------- TB6612 VM
LM LOGICA OUT+ (ajustado a 5 V) ---------- Pico VSYS (39)
Ambos OUT- ----------------------------- GND COMUN
Pico GND (38) -------------------------- GND COMUN
TB6612 todos sus GND ------------------- GND COMUN
Pico 3V3 OUT (36) --------+-------------- TB6612 VCC
                         +-------------- Hall VCC

NO unir OUT+ de 12 V con OUT+ de 5 V.
Conexion directa a VSYS: desconectar los 5 V externos para usar USB.
No conectar 5 V a 3V3. Ajustar ambos bucks antes de conectarlos.
Los LM2596 reducen tension: 12 V de entrada no garantizan 12 V de salida.
Vehiculo: C1442.1 -> fusible + proteccion pendiente -> VIN.
C1442.2 -> GND COMUN. Esta entrada aun no esta validada para el vehiculo.
```

## 2. TB6612 Y MOTOR: RESPETAR LAS ETIQUETAS DEL MODULO REAL

```text
Pico GP2 (4) -------------------- AIN1 + BIN1
Pico GP3 (5) -------------------- AIN2 + BIN2
Pico GP4 (6) -------------------- PWMA + PWMB
Pico GP5 (7) --------+----------- STBY
                     +--[10k]--- GND     (pull-down externo)

AO1 + BO1 ----------------------+---- MOTOR borne 1
                                |
                          [104 / 100 nF]
                                |
AO2 + BO2 ----------------------+---- MOTOR borne 2

104 ceramico >=50 V: directamente en los bornes, patas cortas.
Los bornes del motor NO van a GND. No unir borne 1 y borne 2.
Trenzar entre si los dos cables del motor.
Entradas y PWM de ambos canales unidos fisicamente.
Sin puente fijo entre STBY y VCC.
Verificar desacoplo local del modulo: 100 nF VM-GND y VCC-GND.
470 uF / 35 V disponible: (+) a VM, (-) a GND, junto al driver.
Ese capacitor no sustituye la proteccion de entrada del vehiculo.
```

## 3. HALL SS49E: FILTRO PROBADO

```text
Pico 3V3 (36) --------+---------- Hall VCC
                      |
                   [104] 100 nF     JUNTO AL SENSOR
                      |
Pico AGND (33) -------+---------- Hall GND

Hall OUT ---- cable ----[1k]----+---- Pico GP26 / ADC0 (31)
                               |
                            [103] 10 nF   JUNTO AL PICO
                               |
Pico AGND (33) -----------------+

AGND y GND son la misma red electrica del Pico.
Hall GND vuelve al Pico; no transportar corriente del motor por el.
Llevar OUT junto con el retorno GND del Hall.
Si motor y Hall comparten recorrido, usar pares separados.
Conservar el orden de patas del sensor ya comprobado.
No agregar la resistencia de 100k del esquema antiguo.
A = Hall alto / cerrado. B = Hall bajo / abierto.
Montaje actual: sentido 1 abre B; sentido 2 cierra A.
```

## 4. COMANDO PCM: PC817 Y DIODO ANTIPARALELO

```text
C1442.1 VPWR ----[10k / 1/4 W]----+---- PC817 pata 1 (anodo)
                                 |
                         K [1N4007] A
                                 |
C1442.3 CMCV --------------------+---- PC817 pata 2 (catodo)

Diodo: banda K a pata 1; extremo A a pata 2 del PC817.
Pico GP15 (20) ----------------------- PC817 pata 4 (colector)
Pico GND ---------------------------- PC817 pata 3 (emisor)
GP15 usa PULL_UP interno; no agregar pull-up a 5 V.

PC817 DIP4 visto DESDE ARRIBA, muesca hacia arriba:
                         ___U___
                  A  1  |       |  4  C
                  K  2  |_______|  3  E

C1442.2 PWRGND -> GND COMUN (montaje completo).
C1442.4 CMCVM -> SIN CONECTAR, extremo aislado.
GP18 (24) -> libre: no montar Monitor en esta revision.
El conjunto tiene GND comun; los LM2596 no aportan aislamiento.
```

## 5. INDICADORES OPCIONALES Y MONTAJE SIN PCB

```text
GP16 (21) ----[1k]---- anodo LED VERDE; catodo -> GND
GP17 (22) ----[1k]---- anodo LED ROJO;  catodo -> GND
Los LED requieren programa que los controle; la prueba de banco
actual no los maneja. No indican por si solos posicion confirmada.
GP28 (34) libre: divisor VM no montado en esta revision de banco.

Fijar modulos a una base aislante con separadores y tornillos.
Potencia: cables cortos, borneras/crimpado o uniones soldadas aisladas.
No usar Dupont como conexion permanente de potencia.
Cubrir cada union y pata expuesta con termorretractil.
Sujetarlos para que vibracion y tirones no carguen las soldaduras.
PC817/resistencias: soldadura punto a punto con patas aisladas
individualmente y soporte mecanico; no dejar piezas colgando.
Mantener ajustes y disipadores de los bucks accesibles.
No encerrar modulos calientes en pegamento o termorretractil.
Numeros entre parentesis = pin FISICO del Pico original.
Sin corte por sobrecorriente: PWM/timeout no limitan corriente.
```

## Alcance de alimentacion y software

- Los dos bucks se alimentan desde el mismo VIN; no estan en cascada en este plano.
- El fusible de entrada y la proteccion contra polaridad/transitorios no estan dimensionados aqui. El RL207 y el capacitor disponible no se consideran una proteccion automotriz completa. No se prescribe instalar el RL207 en serie con todo el motor sin verificar su corriente y temperatura.
- La conexion de 5 V a VSYS dibujada no incluye un diodo de aislamiento. Para programar por USB, desconectar fisicamente esa salida de 5 V de VSYS; apagar solo la entrada del buck no equivale a desconectarlo. Conservar GND comun al probar el motor por USB. Si se desea alimentar por USB y buck simultaneamente, implementar primero el circuito de seleccion con Schottky indicado por Raspberry Pi.
- No aumentar los valores de tension de los bucks para compensar caidas. Verificar VM bajo carga. El LM2596 es reductor, no elevador.
- No se agrega el pull-down de 100k al Hall del esquema anterior: las capturas actuales corresponden a resistencia serie de 1k, 103 a AGND y 104 de alimentacion.
- Mantener desacoplo local en el driver; verificar lo que ya incluye el modulo antes de duplicar componentes. El 470uF/35V se propone en VM, no como supresor de transitorios en la entrada de camioneta.
- `prueba_tb6612.py` sigue siendo manual de banco. La opcion `a` usa umbrales A=40000/B=26000, freno de 50 ms y direccion A=-1. `main.py` aun detiene en rueda libre, requiere divisor VM y configuracion final; DRIVE_ENABLED sigue False. Este plano no habilita un arranque autonomo.

Referencias: [Pico, alimentacion VSYS y USB](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf), [TI LM2596](https://www.ti.com/lit/ds/symlink/lm2596.pdf), [supresion de ruido del motor](https://www.pololu.com/docs/0J15/9).
