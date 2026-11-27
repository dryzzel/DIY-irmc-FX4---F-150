> **ARCHIVED / ARCHIVADO:** Earlier revision; not current installation guidance.
> Use [current hardware](../en/hardware.md) / [hardware actual](../es/hardware.md).
> Historical scripts are now in [legacy](../../legacy/README.md).

# Prueba de lectura del comando CMCV

Este documento corresponde a `prueba_entrada.py`, copia del lector original.
El nuevo `main.py` es el controlador completo: ver `ESQUEMA_FINAL.md`.

Ford FX4 2007 5.4 L 3V. Prototipo temporal de lectura, no instalacion definitiva.
No conecta motor, reles, sensor Hall ni Monitor. No reproduce aun el actuador completo.

Pinout C1442 segun el diagrama aportado:
1 VPWR, 2 PWRGND, 3 CMCV, 4 CMCVM.
Estos numeros NO son los numeros de patas del PC817.

## Componentes

- Pico con MicroPython y cable USB.
- PC817 discreto DIP-4 (no un modulo de conexiones desconocidas).
- R1: 10 kohm, 1/4 W, en la entrada; mantiene una carga similar a la prueba anterior.
- D1: 1N4148, antiparalelo al LED del opto.
- Un LED verde y uno rojo, convencionales de baja corriente.
- Dos resistencias de 1 kohm, 1/4 W: una por cada LED indicador.
- Power bank USB para usar el Pico sin PC (sin cargarlo desde la camioneta).

GP15 usa el pull-up interno, activado con `Pin(INPUT_GPIO, Pin.IN, Pin.PULL_UP)`.
No se necesita resistencia externa de 47 kohm ni cable a 3V3 OUT.
R1 sigue siendo necesaria: limita la corriente del LED del PC817.

## Esquema electrico

```text
LADO VEHICULO / FUENTE DE BANCO       | LADO PICO (USB)
                                     |                     3V3 interno del Pico
C1442-1 VPWR --- R1 10k --- A          |                            |
                          |          |                     [pull-up INTERNO]
                   PC817 pata 1      |                            |
                      LED  --> luz --|--> fototransistor           +-- GP15 (fisico 20)
                   PC817 pata 2      |       pata 4 (colector) -----+
                          |          |       pata 3 (emisor) -------- GND (fisico 18)
C1442-3 CMCV ------------- B          |

D1 entre A y B: CATODO (banda) a A; ANODO a B.
C1442-2 y C1442-4 no se conectan al Pico ni al opto en esta prueba.
NO unir GND del Pico a tierra del vehiculo.
```

PC817 DIP-4 visto desde ARRIBA, muesca hacia arriba:

```text
             ___U___
  anodo   1 |       | 4 colector
  catodo  2 |_______| 3 emisor
```

## LEDs de estado (solo lado Pico)

```text
GP16 (fisico 21) ---[1 kohm]--- anodo LED VERDE catodo --- GND Pico
GP17 (fisico 22) ---[1 kohm]--- anodo LED ROJO  catodo --- GND Pico
                                                       (fisico 23)
```

Cada LED tiene su propia resistencia. El catodo suele ser la pata corta y el
lado plano de la capsula; verifica la polaridad si las patas fueron cortadas.
No conectes estos LEDs a 12 V ni a la tierra del vehiculo.

| Indicador | Significado |
|---|---|
| Verde ON | Opto encendido, GP15 LOW: comando a tierra; cierre provisional |
| Rojo OFF | Opto apagado, GP15 HIGH: liberacion O falta de alimentacion/conexion |
| Ambos apagados | Inicio, cambio aun sin estabilizar, programa detenido o Pico sin alimentacion |

ON/OFF describe el opto, no la posicion real de las valvulas ni necesariamente
la etiqueta del escaner. El rojo no confirma apertura fisica.
El programa espera 50 ms de estado estable antes de encender el indicador.

Verifica marca y orientacion contra la hoja de datos de tu pieza antes de conectar.
D1 limita tension inversa sobre el LED; NO constituye proteccion automotriz completa.
Retira la resistencia de la prueba anterior: R1 la sustituye, no se agrega en paralelo.

R1 entrega aproximadamente (13-1.2)/10000 = 1.18 mA. La corriente que debe
absorber el fototransistor depende del pull-up interno; no se presupone una
resistencia exacta de 47 kohm. Sharp especifica el CTR minimo
a 5 mA, no a esta corriente: hay que verificar el funcionamiento de ESTA pieza
en banco; esto no garantiza funcionamiento con temperatura, envejecimiento o transitorios.
No reducir R1 automaticamente si falla la prueba.

## Primera prueba: banco, sin PCM

1. Alimenta el Pico por USB. Usa una fuente independiente de 12 V DC
   (preferentemente limitada en corriente) para el lado de entrada.
2. Con todo apagado, conecta positivo de la fuente al extremo de R1 que representa VPWR.
3. El punto B representa el comando. Con un interruptor, conectalo al negativo
   de ESA fuente para simular tierra; abre el interruptor para simular liberacion.
   Este puente es SOLO de banco: no puentear el comando de la PCM en el vehiculo.
4. No conectes el negativo de esa fuente al GND del Pico.
5. Abre prueba_entrada.py en Thonny con interprete MicroPython (Raspberry Pi Pico) y ejecutalo.
   Solo para volver a esta prueba aislada, guardalo en el Pico como main.py
   (esto sustituye al controlador completo en ese Pico).
6. B a negativo: GP15 debe bajar cerca de 0 V, encender el verde y aparecer CERRAR.
   B abierto: GP15 debe subir cerca de 3.3 V, encender el rojo y aparecer OPTO APAGADO.
   Mide GP15 respecto al GND del Pico en V DC para verificar ambos niveles.
7. Si no obtienes dos niveles claros, detente y revisa polaridad, pinout y tensiones.

## Prueba temporal en el ramal

Solo despues de pasar banco. Con contacto apagado, conecta R1 a C1442-1 y B a
C1442-3. Aisla y sujeta las conexiones. Alimenta el Pico por USB de un power bank
independiente, sin cargarlo desde la camioneta ni otro enlace electrico al vehiculo. Motor y Monitor
permanecen desconectados. No instalar permanentemente ni circular con este montaje.

Para funcionar sin PC, guarda prueba_entrada.py en la RAIZ del Pico con el nombre
exacto `main.py` desde Thonny (guardar solo en el PC no basta). Desconecta el PC
y conecta el power bank: MicroPython ejecutara main.py automaticamente.
Comprueba previamente en banco que ambos estados encienden el LED correcto.
Si el power bank se apaga por bajo consumo, usa su modo de baja corriente
si dispone de el, u otra alimentacion USB independiente que permanezca activa.

Ejecuta el programa y observa las condiciones ya probadas. No se promete que
el comando cambie acelerando en estacionamiento. El usuario ya observo ambos
estados electricos (12-14 V y 1.6 V entre 1 y 3), con GP16/GP17 inicialmente
intercambiados. Esa prueba no valida todavia posicion mecanica ni Monitor.
La prueba no necesita funcionar al arrancar; evita conectar/desconectar con contacto puesto.

| Entrada | GP15 | Interpretacion provisional |
|---|---|---|
| PCM lleva CMCV a tierra | 0 | Cerrar |
| PCM libera CMCV, alimentacion presente | 1 | Abrir |
| Sin VPWR, cable cortado u opto sin conducir | 1 | Indistinguible de liberar con esta sola entrada |

La equivalencia cerrar/abrir procede del texto aportado por el usuario; falta
validar ambos estados en el vehiculo. Este programa NO trata HIGH como una
orden segura para accionar un motor. El controlador final necesitara validacion
de alimentacion, Hall, tiempo de recorrido y corriente, ademas de la interfaz Monitor.

El programa filtra 50 ms, informa cambios y da un resumen cada 2 segundos.
Muestrea cada 5 ms: no detecta todos los pulsos ni sustituye un osciloscopio.
Ctrl+C detiene la lectura y apaga ambos LEDs. Solo GP16 y GP17 son salidas;
no hay salidas de motor ni Monitor. Sin PC, desconecta el USB para apagar el Pico.

## Fuentes y verificacion

- PC817: https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf
- Pico: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- MicroPython RP2: https://docs.micropython.org/en/latest/rp2/quickref.html

Codigo revisado localmente; pendiente ejecutar y verificar niveles en hardware real.
