"""Configuracion de puesta en marcha. None requiere medicion real."""
DRIVE_ENABLED = False
MONITOR_ENABLED = False
OPEN_END = 'B'  # Confirmado mecanicamente: bajo = abierto.
A_DIRECTION = 1  # Cables invertidos al soldar: IN1=1/IN2=0 hacia A cerrado.
MOTION_TIMEOUT_MS = None  # Recorrido medido con margen, en milisegundos.
HALL_A_ENTER = 35150
HALL_A_EXIT = 34150
HALL_B_ENTER = 29150
HALL_B_EXIT = 30150
HALL_MIN = 2000
HALL_MAX = 63500
HALL_STABLE_MS = 30
COMMAND_STABLE_MS = 50
STARTUP_MS = 500
REVERSE_PAUSE_MS = 300
SETTLE_MS = 150
RAMP_MS = 200
PWM_START = 0.25
PWM_RUN = 0.50  # Inicial de banco; torque no garantizado.
PWM_HZ = 20000
VM_MIN = 9.0
VM_MAX = 13.0
VM_DIVIDER = 122.0 / 22.0  # 100k arriba y 22k abajo.
ADC_REFERENCE = 3.3
LOOP_MS = 5
