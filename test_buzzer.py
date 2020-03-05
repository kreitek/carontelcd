#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function, unicode_literals
import RPi.GPIO as GPIO
import time


URL_BASE = "http://demo.galotecnia.com/control/dispositivo/"
URL_TARJETA = URL_BASE + "{mac}/{uid}?t={uptime}"
URL_KEEPALIVE = URL_BASE + "{mac}?t={uptime}"
KEEPALIVE_SECONDS = 300


GPIO.setmode(GPIO.BOARD)  # Use board pin numbering
print("Poniendo pin como salida y apagando")
GPIO.setup(7, GPIO.OUT)  # Setup GPIO Pin 7 to OUT
GPIO.output(7, False)  # Turn on GPIO pin 7
time.sleep(2)

print("Encendiendo pin")
GPIO.output(7, True)  # Turn on GPIO pin 7
time.sleep(1)

print("Apagando pin")
GPIO.output(7, False)  # Turn on GPIO pin 7
time.sleep(1)

print("Finalizando")
GPIO.cleanup()
