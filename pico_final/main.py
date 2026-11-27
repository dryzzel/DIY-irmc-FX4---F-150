"""Instalar como /main.py junto a la carpeta /pico_final/."""
from machine import Pin

# Pines fijos de apagado, incluso si la configuracion no puede importarse.
Pin(18, Pin.OUT, value=0)
Pin(5, Pin.OUT, value=0)
Pin('LED', Pin.OUT, value=0)

from pico_final.runtime import run

run()
