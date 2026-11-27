"""LED integrado: encendido si GP15=0 (PC817 activo), no confirma posicion."""
from machine import Pin

_led = None
_entrada = None


def _actualizar(pin):
    _led.value(pin.value() == 0)


def iniciar(entrada):
    global _led, _entrada
    detener()
    _led = Pin("LED", Pin.OUT, value=0)
    _entrada = entrada
    entrada.irq(handler=_actualizar, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)
    _actualizar(entrada)


def detener():
    global _entrada
    if _entrada is not None:
        _entrada.irq(handler=None)
        _entrada = None
    if _led is not None:
        _led.off()
