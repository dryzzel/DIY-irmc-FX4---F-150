"""Prueba exclusiva del Monitor: cada pulsacion BOOTSEL alterna GP18.

Ejecutar con el automatico desactivado y despues de cortar/reponer alimentacion
para eliminar su watchdog. No importa el controlador ni mueve el motor.
El LED integrado indica GP18, NO la posicion del mecanismo ni el voltaje PCM.
"""
from machine import Pin, PWM
from time import ticks_ms, ticks_diff, sleep_ms
import rp2

REBOTE_MS = 50


def main():
    standby = Pin(5, Pin.OUT, value=0)
    monitor = Pin(18, Pin.OUT, value=0)
    # Desconectar el indicador anterior de GP15 si quedo cargado en el REPL.
    Pin(15, Pin.IN, Pin.PULL_UP).irq(handler=None)
    led = Pin("LED", Pin.OUT, value=0)
    pwm_motor = PWM(Pin(4))
    pwm_motor.duty_u16(0)
    Pin(2, Pin.OUT, value=0)
    Pin(3, Pin.OUT, value=0)
    estado = False
    candidato = bool(rp2.bootsel_button())
    estable = None
    desde = ticks_ms()
    armado = False  # Exige soltar el boton antes de aceptar la primera pulsacion.
    try:
        print("PRUEBA MONITOR: motor deshabilitado. BOOTSEL alterna ON/OFF.")
        print("OFF | GP18=0 | LED apagado | Monitor esperado: ALTO")
        print("El voltaje real se mide con multimetro. Ctrl+C termina.")
        while True:
            standby.off()
            ahora = ticks_ms()
            pulsado = bool(rp2.bootsel_button())
            if pulsado != candidato:
                candidato = pulsado
                desde = ahora
            if ticks_diff(ahora, desde) >= REBOTE_MS and candidato != estable:
                estable = candidato
                if not estable:
                    armado = True
                elif armado:
                    armado = False
                    estado = not estado
                    monitor.value(estado)
                    led.value(estado)
                    if estado:
                        print("ON  | GP18=1 | LED encendido | Monitor esperado: BAJO")
                    else:
                        print("OFF | GP18=0 | LED apagado | Monitor esperado: ALTO")
            sleep_ms(10)
    finally:
        monitor.off()
        standby.off()
        led.off()
        pwm_motor.duty_u16(0)
        pwm_motor.deinit()
        print("Prueba detenida: Monitor OFF y motor deshabilitado.")


if __name__ == "__main__":
    main()
