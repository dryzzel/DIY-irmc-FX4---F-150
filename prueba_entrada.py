"""Prueba CMCV: solo lectura de GP15 mediante PC817, sin salidas de motor."""
from machine import Pin
from time import ticks_ms, ticks_diff, sleep_ms

INPUT_GPIO = 15  # Pin fisico 20. Pull-up interno; sin resistencia externa a 3V3.
GREEN_GPIO = 16  # Pin fisico 21: resistencia 1k + LED verde a GND.
RED_GPIO = 17  # Pin fisico 22: resistencia 1k + LED rojo a GND.
STABLE_MS = 50
REPORT_MS = 2000


def describe(level):
    if level == 0:
        return "OPTO ENCENDIDO | orden provisional: CERRAR"
    return "OPTO APAGADO | ABRIR solo si alimentacion y cableado estan OK"


def main():
    command = Pin(INPUT_GPIO, Pin.IN, Pin.PULL_UP)
    green = Pin(GREEN_GPIO, Pin.OUT, value=0)
    red = Pin(RED_GPIO, Pin.OUT, value=0)
    try:
        read_command(command, green, red)
    finally:
        green.off()
        red.off()


def read_command(command, green, red):
    candidate = command.value()
    since = ticks_ms()
    accepted = None
    last_report = since
    sampled_changes = 0
    print("Prueba de entrada CMCV. Motor y Monitor NO controlados.")
    print("HIGH tambien puede significar desconexion o falta de alimentacion.")
    print("Filtro: 50 ms. Cambios contados por muestreo; no es osciloscopio.")
    while True:
        now = ticks_ms()
        raw = command.value()
        if raw != candidate:
            candidate = raw
            since = now
            sampled_changes += 1
        if ticks_diff(now, since) >= STABLE_MS and accepted != candidate:
            accepted = candidate
            print("[{} ms] GP15={} | {}".format(now, accepted, describe(accepted)))
        # Ambos apagados durante el filtro; nunca mostrar el estado anterior.
        # Apagar primero evita encender ambos al cambiar de estado.
        stable_now = ticks_diff(now, since) >= STABLE_MS
        if stable_now and accepted == 0:
            red.off()
            green.on()
        elif stable_now and accepted == 1:
            green.off()
            red.on()
        else:
            green.off()
            red.off()
        if ticks_diff(now, last_report) >= REPORT_MS:
            stable = accepted if ticks_diff(now, since) >= STABLE_MS else "INESTABLE"
            print("Estado={} | instantaneo={} | cambios muestreados/2s={}".format(
                stable, raw, sampled_changes))
            sampled_changes = 0
            last_report = now
        sleep_ms(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Prueba detenida.")
