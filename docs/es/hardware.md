# Hardware y cableado

[Inicio](../../README.es.md) · [English](../en/hardware.md)

Referencia de señales del montaje del propietario: F-150 FX4 2007, 5.4 L 3V.
Reúne el comando, Hall y Monitor confirmados. No es un esquema de producción
completo: no quedaron registrados todos los detalles de protección de entrada,
valor de fusible, marcas de componentes y fijación mecánica. El propietario
confirmó el 27-11-2026 que estaba instalado y funcionando correctamente por semanas.

## Componentes

| Cantidad | Componente | Función |
| --- | --- | --- |
| 1 | Raspberry Pi Pico RP2040 | Controlador MicroPython; numeración del Pico original |
| 1 | Módulo TB6612FNG | Driver bidireccional, canales sincronizados |
| 2 | LM2596 ajustables | Alimentación nominal 12 V del motor y 5 V de lógica |
| 1 | SS49E lineal | Lectura de los dos imanes originales |
| 2 | PC817 | Entrada PCM y control de la etapa Monitor |
| 1 | KN2222A NPN | Lleva Monitor a tierra |
| 1 | 1N4007 | Protección inversa del LED del opto de entrada |
| 1 de cada uno | Carcasa, engranajes y motor RS-365SH originales | Mecánica reutilizada |
| 4 | Resistencias 10 kΩ | Serie de entrada, pull-down STBY, GP18 y base NPN |
| 4 | Resistencias 1 kΩ | Filtro Hall y tres en serie hacia base NPN |
| 1 | Resistencia 620 Ω | Serie del LED del opto Monitor |
| 1 | Cerámico 10 nF (`103`) | Filtro ADC del Hall |
| Según esquema | Cerámicos 100 nF (`104`) | Hall, motor y desacoplo del driver |
| Según alimentación | Capacitores de reserva y protección | Confirmar posición, polaridad y capacidad |
| Opcionales | LED verde y rojo, cada uno con 1 kΩ | Orden y fallo |

La resistencia serie de entrada se documentó como 10 kΩ de 1/4 W. Dimensionar
las demás potencias según su circuito. Confirmar el orden real de patas de cada
sensor, transistor y módulo; no deducirlo de otro componente parecido.

## Conector de la camioneta

Usar números de cavidad de C1442. La vista del ramal y del actuador se refleja;
no asumir orden izquierda/derecha por una fotografía.

| Cavidad | Señal | Conexión |
| --- | --- | --- |
| 1 | VPWR | Entrada de alimentación protegida y resistencia de comando |
| 2 | PWRGND | Tierra común |
| 3 | CMCV | Comando PCM al cátodo del opto de entrada |
| 4 | CMCVM | Monitor hacia PCM al colector KN2222A |

En este montaje, PCM lleva CMCV a tierra para cerrar y lo libera para abrir.
El opto encendido produce GP15=0. Un cable de comando abierto puede parecer una
orden de abrir: esta entrada no permite distinguirlos.

## Alimentación y tierras

```text
C1442.1 -- fusible / protección (*) --+-- LM2596 motor IN+
                                     +-- LM2596 lógica IN+
C1442.2 -- GND común --------------------+-- ambos IN- / OUT-
                                         +-- GND Pico y todos los GND TB6612
                                         +-- emisor Monitor y retornos

LM motor OUT+ (nominal 12 V) ----------- TB6612 VM
LM lógica OUT+ (5 V) ------------------ Pico VSYS (físico 39)
Pico 3V3 OUT (físico 36) -------------- TB6612 VCC y SS49E VCC
```

`(*)` Esta publicación no define la red exacta de protección de entrada. No es
un puente de cable ni supone que un RL207 y un capacitor equivalgan a protección
automotriz validada. Documentar el circuito realmente utilizado.

Los **OUT+ de 12 V y 5 V no se unen**. Los reguladores y el Pico comparten tierra;
el conjunto no queda aislado galvánicamente por usar optos. El retorno de potencia
del motor va a tierra de potencia, no por AGND del Hall. Al probar con USB se
mantiene GND común entre Pico y driver.

Si el buck está conectado directamente a VSYS, desconectar físicamente ese cable
de 5 V antes de alimentar por USB, salvo que exista selección de fuentes adecuada.
Apagar el buck no equivale a desconectar su salida. Consultar la
[documentación de alimentación del Pico](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf).
No conectar 5 V a `3V3 OUT`.

El LM2596 reduce tensión: si falta margen de entrada no mantiene 12 V de salida.
Medir VM bajo carga y frenado. Su protección interna no establece un límite
de corriente apropiado para el motor/driver. [Datasheet TI](https://www.ti.com/lit/ds/symlink/lm2596.pdf).

## Driver y motor

| Pico / fuente | TB6612 |
| --- | --- |
| GP2 | AIN1 + BIN1 |
| GP3 | AIN2 + BIN2 |
| GP4 | PWMA + PWMB |
| GP5 | STBY y resistencia 10 kΩ a GND |
| 3,3 V | VCC |
| Buck motor | VM |
| GND común | Todos los GND |
| Motor borne 1 | AO1 + BO1 |
| Motor borne 2 | AO2 + BO2 |

Confirmar etiquetas del módulo real: BO1/BO2 estaban en otro orden respecto a un
diagrama de internet. Unir entradas y PWM correspondientes antes de unir salidas.
Si se cruzan, los puentes pueden enfrentarse y calentarse. Esto documenta el
montaje utilizado; no garantiza duplicar corriente continua/pico. Ambos canales
comparten los límites térmicos del mismo chip.

Cerámico 100 nF entre bornes del motor con patas cortas y tensión adecuada
(se recomendó al menos 50 V). Ningún borne del motor se conecta directamente a GND.
Verificar desacoplo local VM/GND y VCC/GND. Las notas propusieron 470 µF/35 V en VM;
su posición exacta instalada no se afirma aquí. No sustituye un supresor de picos.

## Hall

```text
Pico 3V3 -------------+----- SS49E VCC
                       |
                     100 nF (104), junto al sensor
                       |
Pico AGND ------------+----- SS49E GND

SS49E OUT ---- 1 kΩ ---+----- GP26 / ADC0
                       |
                      10 nF (103), junto al Pico
                       |
Pico AGND ------------+
```

AGND es físico 33; GP26 es físico 31. Llevar señal Hall junto a su retorno aunque
comparta recorrido con los cables del motor. No montar el pull-down de 100 kΩ de
un esquema antiguo. El Hall se alimenta a 3,3 V; no aplicar 5 V al ADC.

## Opto de comando PCM

```text
C1442.1 VPWR -- 10 kΩ / 0,25 W -- PC817 #1 pin 1, ánodo LED
C1442.3 CMCV ------------------- PC817 #1 pin 2, cátodo LED
1N4007 en antiparalelo: banda/cátodo a pin 1; ánodo a pin 2.
PC817 #1 pin 4, colector ------- GP15, pull-up interno a 3,3 V
PC817 #1 pin 3, emisor --------- GND común
```

No conectar tensión PCM directamente a GPIO ni elevar GP15 a 5 V. En PC817 DIP-4
los pines 1/2 son LED y 4/3 colector/emisor; identificar su marca de pin 1.

## Etapa Monitor

```text
GP18 -- 620 Ω ----------------- PC817 #2 pin 1, ánodo LED
GND --------------------------- PC817 #2 pin 2, cátodo LED
GP18 -- 10 kΩ -- GND

+5 V regulados ---------------- PC817 #2 pin 4, colector
PC817 #2 pin 3, emisor -- 1 kΩ -- 1 kΩ -- 1 kΩ -- base KN2222A
Base KN2222A -- 10 kΩ -- GND
Emisor KN2222A ---------------- C1442.2 / GND común
Colector KN2222A -------------- C1442.4 CMCVM
```

La PCM aporta el voltaje alto. El circuito solo lleva Monitor a tierra: no conectar
la salida de 5 V ni de 12 V del regulador a CMCVM. GP18=1 da bajo/ABIERTO; GP18=0
libera la línea, alto interpretado como CERRADO. Alto durante movimiento/fallo
no confirma cierre físico. Las pruebas reportaron aproximadamente 12 V liberado
y 0 V activado con la PCM conectada.

Verificar emisor/base/colector del KN2222A exacto. Invertir emisor y colector causó
una prueba fallida durante el desarrollo. Retirar cualquier pull-up externo
temporal de banco antes de conectar PCM. [Prueba aislada](../../examples/README.md).

## Indicadores y entradas libres

GP16 -> 1 kΩ -> ánodo LED verde; cátodo a GND: orden estable de cerrar.
GP17 -> 1 kΩ -> ánodo LED rojo; cátodo a GND: abrir; parpadea en fallo.
Indican orden, no una medición independiente de posición. GP27/GP28 no miden
corriente ni VM. El LED integrado queda apagado.

No se entregan archivos de fabricación PCB ni plano verificado por agujeros.
Los [diagramas archivados](../archive/README.md) representan revisiones anteriores.
