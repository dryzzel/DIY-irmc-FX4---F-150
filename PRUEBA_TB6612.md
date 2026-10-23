# Prueba manual de giro con TB6612FNG

## Diagnostico actual tras remontaje / timeout de r

Usar t desde centro, primero sentido 1. Preparar posicion con VM apagada y Hall
por USB; despues restablecer VM, elegir t y sentido. Cuenta regresiva de 3 s,
validacion del centro y un solo movimiento limitado a 1000 ms. No ampliar timeout.
Esta prueba corta al encontrar A O B, aunque sea contrario al sentido esperado.
Conservar conexiones actuales para diagnosticar; no requiere agregar condensadores.

Al terminar imprime min/max de promedios y muestras crudas DURANTE el ensayo,
antes del freno, ademas del intervalo maximo de lectura. Estos valores tambien
se imprimen si hay timeout, ADC fuera de rango o Ctrl+C tras iniciar el muestreo.
Una lectura fuera de rango ahora incluye sus valores exactos. No imprime mientras
gira. El resumen queda en consola; no modifica hall_recorrido.json.
El archivo local usa PWM_FINAL=0.60: al copiarlo al Pico el diagnostico sera al 60%,
no al 80% que el usuario habia ajustado en su otra copia. Se imprime el PWM real.
Si no detecta ninguno, no repetir con mas tiempo: compartir todo el resumen.

## Ensayo actual: frenado electrico en extremos (a, r, t)

Al llegar al umbral Hall, se aplica short brake durante FRENO_MS=50 ms y despues
se deshabilita STBY. Se conserva PWM maximo 60%, umbrales y timeouts anteriores.
Preparacion del freno: STBY=0, PWM=0, IN1=IN2=1; finalmente STBY=1.
Ambos canales reciben las mismas senales por los puentes ya verificados.
Esta es una duracion inicial experimental, no una garantia de parada ni de corriente.

La funcion parar() sigue siendo rueda libre. Timeout, error y cancelacion no
inician frenado; deshabilitan el driver. Las opciones 1/2/g/c no cambian su parada.
En a solo se frena al alcanzar el destino mientras estaba moviendo, nunca en
la pausa al abandonar el extremo de origen; una nueva orden o fallo cancela el
pulso de frenado. No hay frenado permanente para mantener posicion.

En r, tiempo cero de las muestras es el inicio del freno: la muestra inicial
se toma durante el freno; a 100/300/700 ms ya esta en rueda libre. El JSON agrega
freno_ms por tramo. Si no llega por Hall, freno_ms=0. Se conservan los tiempos
reales de cada muestra. La lectura Hall continua durante el frenado.

Probar primero un ciclo r y comparar Hall al corte, valores posteriores y
retencion. Cortar potencia si aparece ruido o calentamiento anormal. No hay
sensor de corriente de frenado; el ensayo previo de giro no valida esta corriente.
Solo cambia prueba_tb6612.py: main.py y el controlador final no aplican este freno.
Las menciones de rueda libre inmediata en secciones anteriores describen la
version previa; para a/r/t esta seccion define la secuencia actual.

Referencia short brake: tabla H-SW Control Function, pagina 4:
https://toshiba.semicon-storage.com/info/docget.jsp?did=10660&prodName=TB6612FNG

## Diagnostico de sobrepaso al 60% PWM

a, r y t usan ahora una espera de 1 ms entre ciclos Hall. Esto NO garantiza
muestreo a 1 kHz: hay tiempo adicional de ADC, interprete e interrupciones.
a no imprime mientras STBY esta activo. Tras cada corte muestra Hall y mayor
intervalo medido entre lecturas del segmento de movimiento, en milisegundos.
r agrega intervalo_hall_max_ms por tramo al JSON. Mantiene muestras despues
del corte para distinguir cruce tardio del umbral de desplazamiento posterior.
No se modifican potencia, umbrales, timeout ni parada en rueda libre.
El filtro de estabilidad no mantiene el motor encendido esperando confirmar
el destino: una transicion de Hall en a ya produce corte. Puede tambien generar
una pausa al abandonar el extremo de origen, comportamiento aun conservado.
Los cambios mejoran la latencia de software; no garantizan eliminar la inercia.

## Control automatico de banco por PC817: opcion a

Copiar al Pico las versiones actuales de `prueba_tb6612.py`, `controller.py` y
`config.py`. Ejecutar prueba_tb6612.py, no main.py. La opcion a habilita movimiento
solo durante esta sesion; no modifica config.py ni habilita arranque automatico.

Motor con engranajes, SS49E instalado y PC817 en GP15, como en las pruebas previas.
Monitor queda fuera del ensayo, deshabilitado. No es requisito para continuar.
No se requiere montar divisor VM en GP28 para a: la supervision de tension esta
explicitamente desactivada en esta opcion y no se genera una lectura ficticia.
La alimentacion debe estar verificada externamente. main.py conserva su supervision
de VM y sus valores/configuracion anteriores; no es aun el modo utilizado aqui.

Elegir a: cuenta regresiva de 3 s, sin palabra de confirmacion. Puede moverse
inmediatamente despues segun la entrada inicial:

| Entrada | Destino |
|---|---|
| PC817 encendido / GP15=0 | A cerrado, sentido 2 |
| PC817 apagado / GP15=1 | B abierto, sentido 1 |

Se usa el controlador con umbrales 40000/35000 y 26000/31300, PWM 25%-60%,
timeout provisional 2000 ms, filtro de entrada y pausa de inversion. Al alcanzar
un extremo corta y comprueba asentamiento; no mantiene corriente en el motor.
Cambiar la entrada con el circuito PC817 ya probado, nunca aplicar 12 V a GP15.
Primero alternar despues de ver DETENIDO; luego comprobar que mantener la orden
no produce movimiento repetido. La apertura de un cable puede parecer orden de abrir.

Ctrl+C apaga y vuelve al menu. Timeout, perdida de posicion o Hall invalido
detienen la sesion: no se reintenta automaticamente ni cambiando la entrada.
Volver a seleccionar a inicia una sesion nueva, solo tras revisar el fallo.
Sin watchdog, medicion de corriente ni supervision de VM en este menu de banco.
No sustituye la validacion posterior con la carga de valvulas de la camioneta.

## Dos imanes y medicion despues de parar: opcion r

Direccion confirmada tras el montaje permanente: 1 abre hacia B, 2 cierra hacia A.
Las pruebas a y r usan DIRECCION_A = -1. Verificar t en sentido 2 desde centro
antes de repetir r: debe cortar en A alto. config.py conserva DRIVE_ENABLED=False.
La opcion r no pide palabras: al elegirla hay 3 s de cuenta regresiva y arranca
si el Hall inicial permanece estable. Mantener manos fuera de la mecanica.
Hall y motor deben estar montados como en los ensayos t; no forzar topes duros.

- Si empieza en A, realiza B y luego A. Si empieza en B o centro, realiza A y B.
- Desde el centro, el primer tramo es parcial; el segundo va entre extremos.
  Desde un extremo, ambos tramos son entre extremos. Solo dos destinos, sin bucle.
- Rampa PWM 25% a 60%, sin frenado activo. Corta al umbral de destino:
  A >=40000, B <=26000. El umbral del extremo de partida no impide salir de el.
- Timeout provisional de 2500 ms POR TRAMO completo (los 1000 ms de t se conservan).
  No deriva un tiempo definitivo de los ensayos centro-extremo; no limita corriente.
- Con STBY=0 registra Hall inmediatamente y a 100, 300 y 700 ms despues del corte,
  ademas de min/max durante la observacion. Imprime tiempos reales de muestreo.
- Si hay timeout, lectura ADC invalida, cancelacion o perdida de la zona Hall del
  destino tras 100 ms, detiene el ensayo completo sin invertir ni reintentar.
  Retencion provisional en r: A >=35000, B <=31300 (histeresis); no prueba posicion mecanica.
  En a, el controlador exige A >35000 y B <31300; la igualdad sale de retencion.
- Cada inversion tiene al menos 700 ms de observacion apagado y 500 ms de pausa.
- Guarda `hall_recorrido.json` en el Pico, reemplazando el informe anterior.
  Incluye indicador completo/error y tramos terminados. Si se interrumpe un tramo
  antes de medir su parada, ese tramo puede no aparecer en el archivo.

Estas lecturas permiten observar cambio de campo tras cortar, no medir distancia
ni certificar que el mecanismo este totalmente abierto/cerrado. Cortar potencia
si golpea un tope, se atasca o hace ruido anormal; Ctrl+C apaga por software.

Se retiraron las palabras LIBRE de g y CENTRO de t. Ambas conservan sus requisitos
fisicos y t la comprobacion automatica del centro. c conserva SEPARADOS.
h conserva Enter para indicar cuando cada posicion esta lista para capturar.

## Identificar direccion con topes Hall: opcion t

Datos del aprendizaje aportado: centro 31830; extremo 1 bajo 21309 = B ABIERTO;
extremo 2 alto 48010 = A CERRADO. Se usan umbrales provisionales B <=26000,
A >=40000 SOLO para esta prueba. No modifica config.py ni el controlador final.

1. Con potencia motor quitada y Hall alimentado, verificar a mano que estos
   niveles se alcanzan antes de los topes mecanicos duros, en el montaje final.
   No forzar engranajes para mover el mecanismo. Los umbrales no garantizan
   posicion mecanica exacta ni frenado: STBY=0 deja rueda libre y puede haber inercia.
2. Colocar en centro (Hall entre 30000 y 34000), acoplar mecanica correctamente,
   fijar carcasa y retirar manos. Restablecer VM con el programa detenido en menu.
3. Ejecutar t, elegir sentido electrico 1 (sin confirmacion por palabra). El programa verifica
   el centro durante 500 ms antes de arrancar; si no coincide no mueve.
4. Gira con rampa 25% a 60%, leyendo Hall cada ciclo (~2 ms mas conversiones).
   Corta al primer umbral A/B, lectura ADC fuera de rango, Ctrl+C, error o timeout
   de 1000 ms (1 segundo). La comprobacion de estabilidad de 100 ms ocurre con motor apagado.
5. Copiar Hall inicial, Hall al corte, tiempo y candidato A_DIRECTION. Confirmar
   visualmente el sentido. Un timeout o lectura no sostenida no identifica direccion.
   No aumenta duracion ni repite automaticamente. No es limitador de corriente.
6. Para repetir en sentido 2, quitar VM y volver al centro manualmente; no usar
   1, 2 o g para reposicionar con engranajes acoplados: esas opciones NO usan Hall.

Motor y Monitor del controlador final siguen deshabilitados. Si se altera el
cableado M1/M2 tras esta prueba, hay que volver a identificar la direccion.
Esta prueba no detecta un Hall averiado que entregue un valor plausible fijo:
solo el timeout detendria ese caso. Cortar potencia ante atasco o ruido anormal.

## Aprendizaje manual Hall: opcion h

Desconectar potencia VM del motor y alimentar Pico por USB. Hall a 3.3 V,
GND a AGND y salida por 1k a GP26, con filtros del esquema. Mantener el sensor
en su ubicacion/distancia final frente al disco; no forzar engranajes para moverlo.

Ejecutar `h`. Pide tres posiciones, cada una confirmada con Enter:

1. Centro del recorrido, sin iman enfrentado directamente al sensor.
2. Primer extremo, con su iman frente al sensor.
3. Segundo extremo, con el otro iman frente al sensor.

Mantener inmovil durante cada captura de aproximadamente 2 s. Cada valor es
el promedio de ocho lecturas; se informan media, minimo, maximo y variacion.
El voltaje mostrado usa 3.3 V nominal y es aproximado. `q` cancela entre capturas;
Ctrl+C cancela en cualquier momento. El motor y Monitor permanecen deshabilitados.

Las capturas completas se guardan en `hall_aprendizaje.json` en el dispositivo
que ejecuta el programa, reemplazando el registro anterior. Una cancelacion antes
de guardar conserva el archivo anterior, que no debe confundirse con datos nuevos.
Si hay solapamiento o lecturas cerca de los rieles ADC, se guarda marcado para revisar.
El extremo de lectura alta es candidato A y el de lectura baja candidato B, solo
si sus rangos quedan separados del centro. Esto no identifica Norte/Sur ni
abierto/cerrado. No modifica config.py ni habilita movimiento automatico.
Compartir los tres resultados; repetir para evaluar reproducibilidad antes de
fijar umbrales. Estas capturas estaticas no prueban todo el recorrido ni el ruido
con el motor funcionando.

Ejecutar `prueba_tb6612.py` desde el editor conectado al Pico. No sustituir
`main.py` ni cambiar `DRIVE_ENABLED` para esta prueba. No requiere Hall,
divisor VM ni etapa Monitor. El PC817 solamente se lee a peticion.

## Antes de aplicar potencia

- Motor libre/desacoplado de engranajes y valvulas. Sin Hall, el programa no
  reconoce los topes: esta prueba comprueba giro, no un recorrido del actuador.
- GP2 (4) a AIN1 y BIN1; GP3 (5) a AIN2 y BIN2.
- GP4 (6) a PWMA y PWMB; GP5 (7) a STBY, con 10k entre STBY y GND.
- VCC del driver a 3V3 OUT (36), VM a la salida de alimentacion del motor.
  Verificar VM con multimetro antes de conectar; no conectar bateria cruda a VM.
- AO1 y BO1 unidos al terminal M1; AO2 y BO2 unidos al terminal M2.
- GND de Pico, driver y fuente unidos; potencia por cables/borneras externos
  a la protoboard. Mantener desacoplos del esquema final.
- GP15 a colector PC817 (4); emisor (3) a GND. Se usa pull-up interno.
- Dejar C1442-4 Monitor desconectado durante esta prueba.

## Ejecucion

1. Con potencia del motor desconectada, detener el `main.py` que se este ejecutando.
   Si su watchdog sigue reiniciando el Pico, interrumpirlo al arrancar con el editor
   y reiniciar el interprete antes de lanzar esta prueba. No ejecutar dos programas.
2. Abrir y ejecutar `prueba_tb6612.py`; debe aparecer el menu sin movimiento.
3. Aplicar alimentacion del motor ya verificada.
4. Escribir `1` y Enter: un pulso de 150 ms en sentido 1.
5. Esperar que el eje se detenga; escribir `2` y Enter: sentido contrario.
6. `s` muestra GP15 y el estado del opto sin mover el motor. `0` termina.

Cada pulso incluye una pausa inicial de 500 ms y una rampa PWM de 25% a 60%
durante los primeros 75 ms. Al terminar, STBY baja y el motor queda en rueda
libre; no hay frenado activo. Los sentidos 1/2 aun no equivalen a abierto/cerrado.

Ctrl+C intenta detener mediante `finally`; quitar potencia es el paro independiente
del software. Este ensayo no tiene watchdog ni deteccion de atasco/sobrecorriente.
Los 150 ms son una duracion de prueba, no una garantia de supervivencia del driver.
Si solo zumba o no gira, desconectar y revisar alimentacion/cableado; no insistir
con pulsos ni subir PWM automaticamente. Registrar que ocurre en cada sentido
y la tension VM durante el intento para decidir el siguiente ajuste.

No es necesario cambiar ni conectar la PCM para comprobar los dos sentidos.

## Giro de 2 segundos: opcion g

Tras comprobar los pulsos, usar `g` para un giro mas largo SIN carga mecanica.
Con potencia apagada, comprobar AO1+BO1 a M1 y AO2+BO2 a M2 usando las etiquetas
reales del modulo (no un pinout de internet visto desde otra cara).
Motor conectado electricamente, pero desacoplado de engranajes/valvulas y con
eje libre; fijar el cuerpo para que no se desplace. No sujetar el eje con la mano.

Ejecutar `g`, elegir `1` o `2` sin confirmacion por palabra. Hay cuenta regresiva de 3 s,
pausa de 500 ms y giro de 2 s con rampa de 25% a 60% en 200 ms. Luego STBY=0
y espera de 10 s antes de volver al menu. No hay repeticion ni inversion automatica.
Probar el otro sentido solo si el anterior fue normal y el eje ya se detuvo.
Ctrl+C apaga las salidas por software; cortar potencia ante atasco, olor o
calentamiento anormal. No se mide corriente ni temperatura y el PWM no las limita.

Registrar giro en ambos sentidos y comportamiento del driver. Esto verifica
funcionamiento basico sin carga; no valida capacidad con engranajes, bloqueo,
temperatura prolongada ni funcionamiento instalado en la camioneta.
La opcion `c` sigue siendo exclusivamente SIN MOTOR.

## Diagnostico tras calentamiento: opcion c, solo sin motor

La opcion m de 30 segundos queda deshabilitada. Ejecutar la version actualizada.
Con todo apagado: retirar ambos cables del motor y separar AO1 de BO1 y AO2 de BO2.
Mantener entradas comunes y GND comun entre Pico, driver y negativo de fuente.
Las cuatro salidas deben estar independientes y sin carga.

Primero ejecutar el programa con USB y luego aplicar VM mientras espera en el menu
(STBY=0). Si el driver hace ruido o calienta en reposo, cortar potencia y no ejecutar c.
Si la fuente tiene limite ajustable, usarlo para este ensayo sin carga.

Colocar el multimetro en voltaje DC, punta negra a GND del driver, roja a AO1.
Elegir c y escribir SEPARADOS. Hay una cuenta regresiva de 10 segundos con
STBY=0 para colocar las puntas. Luego aparece MIDE AHORA y una cuenta de
10, 9, ... 1 segundos restantes. Ctrl+C cancela en ambas etapas.
La salida permanece activa al 100% durante 10 s
(IN1 alto, IN2 bajo, STBY alto) y se apaga automaticamente. Repetir para BO1
solo si no hubo calentamiento/ruido. Nunca unir salidas mientras este alimentado.
Diez segundos no garantizan proteger un chip averiado. Cortar potencia ante ruido
 o calentamiento; no esperar al fin del temporizador.

Esperados durante c: STBY/PWMA/PWMB/AIN1/BIN1 ~3.3 V; AIN2/BIN2 ~0 V;
AO1/BO1 ~VM; AO2/BO2 ~0 V. Medir cada salida por separado respecto a GND.
La prueba activa ambos canales con controles comunes pero salidas separadas;
no es una habilitacion independiente de cada canal ni prueba capacidad bajo carga.

Tabla logica: https://toshiba.semicon-storage.com/info/docget.jsp?did=10660&prodName=TB6612FNG

## Ajuste de fuerza en banco

PWM_FINAL sube a 0.60 en prueba_tb6612.py, incluido el modo automatico a.
Se conservan rampa desde 25%, umbrales, timeout y parada en rueda libre.
config.py conserva su valor anterior para main.py, que no es el programa usado
en esta prueba. Los tiempos y posiciones posteriores al corte deben volver a
observarse al 60%; no aumenta la fuerza de retencion estando apagado.
