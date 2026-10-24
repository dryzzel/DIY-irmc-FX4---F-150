"""Copiar al Pico con el nombre main.py SOLO para la prueba temporal."""
from machine import Pin
Pin(5, Pin.OUT, value=0)
Pin(18, Pin.OUT, value=0)
from prueba_camioneta import ejecutar
ejecutar()
