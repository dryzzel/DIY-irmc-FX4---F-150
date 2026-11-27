"""Configuración efectiva del IMRC; no se sobrescribe al arrancar.

Unidades: MS = milisegundos (1000 ms = 1 s), HZ = ciclos por segundo.
True = habilitado; False = deshabilitado.
Los niveles digitales 0/1 significan bajo/alto en el GPIO del Pico.
Los números PIN_* son GPIO (GP), NO números de patilla física del conector.
"""

# Identificación y funciones habilitadas.
VERSION = 'final-1'  # Nombre que aparece en consola; no modifica el funcionamiento.

# True: permite mover el motor. False: modo DIAGNOSTICO, motor y Monitor apagados.
DRIVE_ENABLED = True

# True: permite GP18=1 SOLO al confirmar apertura asentada, sin marcha ni freno.
# False: mantiene GP18=0 y libera la línea Monitor hacia la PCM en todo momento.
# GP18=1 -> transistor conduce -> Monitor BAJO (~0 V), informa ABIERTO.
# GP18=0 -> transistor no conduce -> la PCM eleva Monitor, convención CERRADO.
# Un nivel alto durante movimiento o fallo no prueba que esté cerrado físicamente.
MONITOR_ENABLED = True

# False: no mide la alimentación VM del motor. Este montaje no tiene esa medida.
# True NO habilita una medida por sí solo: la versión actual bloquea el arranque
# con VM_NO_INSTALADO; requiere agregar el circuito y adaptar el programa.
VM_MONITOR_ENABLED = False

# A = extremo de lectura Hall ALTA; B = extremo de lectura Hall BAJA.
# 'B': B es ABIERTO y A CERRADO (montaje actual).
# 'A': A sería ABIERTO y B CERRADO; intercambia los destinos de apertura/cierre.
# En ambos casos GP15=1 ordena ABRIR y GP15=0 ordena CERRAR.
OPEN_END = 'B'

# Sentido eléctrico para alcanzar A; para alcanzar B se usa el contrario.
#  1: hacia A con IN1=1 e IN2=0; hacia B con IN1=0 e IN2=1.
# -1: hacia A con IN1=0 e IN2=1; hacia B con IN1=1 e IN2=0.
# Solo acepta 1 o -1, NO 2. El sentido 2 del menú de pruebas equivale a -1.
# Si se invierten los dos cables del motor, se invierte este signo.
A_DIRECTION = 1

# Tiempo máximo de marcha acumulada por orden estable: 3000 ms = 3 s.
# Se reinicia al confirmar otro destino o completar una llegada asentada.
# No cuenta pausas ni freno; ruido, pausas y reinicios de rampa no lo renuevan.
# Al agotarse sin llegar, apaga el motor y entra en recuperación por TIMEOUT.
MOTION_TIMEOUT_MS = 3000

# PWM se expresa como fracción: 0.40 = 40 %, 0.70 = 70 %, 1.00 = 100 %.
# Es el porcentaje de tiempo de activación, NO un límite de corriente.
PWM_START = 0.40  # PWM al iniciar cada tramo de marcha, también tras una pausa.
PWM_RUN = 0.70  # PWM de marcha alcanzado al terminar la rampa; debe ser >= PWM_START.
RAMP_MS = 20  # Duración del aumento gradual de PWM_START a PWM_RUN (0,020 s).
PWM_HZ = 20000  # Frecuencia PWM del driver: 20 000 Hz = 20 kHz.

# Duración del freno eléctrico al detectar el extremo de destino.
# Después deshabilita el driver y queda en rueda libre; no mantiene fuerza fija.
BRAKE_MS = 50

# Pausa sin accionar el motor antes de arrancar, invertir o reanudar después
# de una interrupción del control por señal/posición no confirmada: 0,3 s.
REVERSE_PAUSE_MS = 300

# Hall: cuentas de ADC.read_u16(), escala 0..65535; NO voltios ni grados.
# ENTER identifica la llegada; EXIT conserva esa posición con un margen
# (histéresis) para tolerar pequeñas variaciones/juego sin perderla enseguida.
HALL_A_ENTER = 40000  # Lectura >=40000 entra en A y permite cortar marcha hacia A.
HALL_A_EXIT = 35000  # Estando en A, se conserva A mientras la lectura sea >35000.
HALL_B_ENTER = 26000  # Lectura <=26000 entra en B y permite cortar marcha hacia B.
HALL_B_EXIT = 31300  # Estando en B, se conserva B mientras la lectura sea <31300.

# Límites de validez eléctrica del Hall, distintos de los umbrales de llegada.
# Cualquier muestra cruda <=MIN o >=MAX provoca HALL_INVALIDO, aunque la media
# parezca normal. Debe cumplirse MIN < B_ENTER < B_EXIT < A_EXIT < A_ENTER < MAX.
HALL_MIN = 2000  # Límite inferior permitido, exclusivo.
HALL_MAX = 63500  # Límite superior permitido, exclusivo.

# Tiempo que debe mantenerse la misma clasificación A/B/MID para confirmarla.
# No exige una lectura numérica idéntica. El corte/freno por umbral puede
# ocurrir antes de completar esta confirmación de posición.
HALL_STABLE_MS = 30

# Tiempo sin cambios del nivel GP15 para aceptar una orden de la PCM.
# 0 = PC817 encendido, CERRAR; 1 = PC817 apagado, ABRIR.
# Un cambio transitorio no confirmado no renueva el timeout de la maniobra.
COMMAND_STABLE_MS = 50

# Validación inicial del controlador: 500 ms = 0,5 s, más los filtros/pausas
# necesarios. También se aplica al crear un controlador tras una recuperación.
# No existe la antigua espera adicional de 5 segundos.
STARTUP_MS = 500

# Tiempo de permanencia en el destino confirmado antes de declarar DETENIDO.
# La confirmación se reinicia si comando/Hall pierden estabilidad. El Monitor
# solo puede activarse tras asentarse y terminar el freno, estando abierto.
SETTLE_MS = 150

# Cantidad de lecturas ADC consecutivas para cada promedio del Hall (1..32).
# Además de promediarlas, comprueba los extremos crudos para detectar fallos.
HALL_SAMPLES = 8

# Espera entre vueltas del control: 1 ms. El intervalo real también incluye
# lectura ADC y ejecución de código; no garantiza una lectura exactamente cada ms.
LOOP_MS = 1

# Espera con motor y Monitor apagados después de timeout, Hall inválido,
# pérdida de posición, excepción o reinicio por watchdog: 30 000 ms = 30 s.
# Los intentos de recuperación no tienen límite; no hay sensor de corriente.
RECOVERY_WAIT_MS = 30000

# Después de la espera, exigir este tiempo continuo de Hall dentro de rango
# y comando GP15 sin cambios antes de crear un controlador nuevo: 1 s.
# No exige Hall inmóvil ni estar frente al imán. Si falla la validación, empieza
# de nuevo este segundo de comprobación; aún no se permite mover el motor.
RECOVERY_VALID_MS = 1000

# Watchdog: reinicia el Pico si el programa deja de alimentarlo durante 1 s.
# Detecta un programa bloqueado; es independiente del timeout de movimiento.
# Tras ese reinicio se aplica la espera de recuperación antes de volver a actuar.
WATCHDOG_MS = 1000

# Intervalo entre encendido/apagado del LED rojo durante fallo/recuperación.
# 250 ms encendido + 250 ms apagado = un ciclo de parpadeo de 500 ms.
FAULT_BLINK_MS = 250

# Máximo de mensajes pendientes de consola en RAM, sin archivos en flash.
# Si se llena, descarta el más antiguo; no detiene el control por llenar la cola.
# Los mensajes se imprimen únicamente cuando no hay marcha ni freno.
CONSOLE_PENDING = 16

# GPIO del montaje soldado. La validación exige estos números concretos;
# cambiarlos requiere adaptar también el cableado y el apagado de emergencia.
# Los dos canales del TB6612 reciben las mismas entradas y PWM.
PIN_STBY = 5  # GP5 -> STBY: 0 deshabilita el puente; 1 permite marcha o freno.
PIN_MONITOR = 18  # GP18 -> opto/transistor: 1 lleva Monitor a tierra; 0 lo libera.
PIN_IN1 = 2  # GP2 -> AIN1 y BIN1; primera entrada de sentido (ver A_DIRECTION).
PIN_IN2 = 3  # GP3 -> AIN2 y BIN2; segunda entrada de sentido (ver A_DIRECTION).
PIN_PWM = 4  # GP4 -> PWMA y PWMB unidos; regula la activación del motor.
PIN_COMMAND = 15  # GP15 <- PC817 de comando; entrada con pull-up interno a 3,3 V.
PIN_HALL = 26  # GP26/ADC0 <- salida filtrada del SS49E, alimentado a 3,3 V.
PIN_GREEN = 16  # GP16 -> LED verde: encendido con orden estable de CERRAR.
PIN_RED = 17  # GP17 -> LED rojo: orden estable de ABRIR; parpadeo si hay fallo.

# El LED integrado queda apagado y BOOTSEL no acciona motor ni Monitor.
