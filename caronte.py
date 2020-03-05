#!/usr/bin/env python
# -*- coding: utf8 -*-

# - rojo marron
# - naranja amarillo

from __future__ import print_function, unicode_literals
import I2C_LCD_driver
import MFRC522
import requests
import RPi.GPIO as GPIO
import signal
import time
import datetime


URL_BASE = "https://metaespacio.kreitek.org/caronte/"
URL_TARJETA = URL_BASE + "{mac}/{uid}?t={uptime}"
URL_KEEPALIVE = URL_BASE + "{mac}?t={uptime}"
KEEPALIVE_SECONDS = 300


class Fichador:
    def __init__(self):
        self.lcd = I2C_LCD_driver.lcd()
        self.reader = MFRC522.MFRC522()
        self.encendido = None
        self.mac = "21B6232DE6B4"
        self.numero_lineas = 2
        self.lineas = []
        self.keepalive = None

        GPIO.setmode(GPIO.BOARD)  # Use board pin numbering
        GPIO.setup(7, GPIO.OUT)  # Setup GPIO Pin 7 to OUT
        GPIO.output(7, False)  # Turn on GPIO pin 7

    def beep(self, sleep=0.05):
        GPIO.output(7, True)
        time.sleep(sleep)
        GPIO.output(7, False)

    def agrega(self, *mensajes):
        self.lcd.backlight(1)
        if len(mensajes) > 1:
            for mensaje in mensajes:
                self.lineas.append(mensaje[:16])
        else:
            mensaje = mensajes[0]
            for i in range(0, len(mensaje), 16):
                self.lineas.append(mensaje[i:i+16])
        self.encendido = time.time()

    def muestra(self):
        vacia = 16 * " "
        for i in range(self.numero_lineas):
            if len(self.lineas) > i:
                mensaje = self.lineas[i]
                mensaje += (16 - len(mensaje)) * " "  # completar con espacios
                self.lcd.lcd_display_string(mensaje, i+1)
            else:
                self.lcd.lcd_display_string(vacia, i+1)

    def borra(self):
        self.lcd.lcd_clear()
        self.lcd.backlight(0)
        self.lineas = []
        self.encendido = None

    def lee(self):
        (status, tag_type) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status != self.reader.MI_OK:
            return None
        (status, uid) = self.reader.MFRC522_Anticoll()
        if status != self.reader.MI_OK:
            return None
        uid_str = "{:2x}{:2x}{:2x}{:2x}".format(*uid).upper()
        print("tag type =", tag_type, "Uid =", uid_str)
        return uid_str

    def uptime(self):
        seconds = open("/proc/uptime").read().split(" ")[0]
        return int(float(seconds))

    def do_keepalive(self):
        if not self.keepalive or time.time() - self.keepalive > KEEPALIVE_SECONDS:
            url = URL_KEEPALIVE.format(mac=self.mac, uptime=self.uptime())
            print("keepalive = ", url)
            r = None
            try:
                r = requests.get(url)
            except requests.exceptions.ConnectionError as e:
                self.agrega(str(e))
            if r:
                if r.status_code != 200:
                    self.agrega("algo fallo", "status code: {}".format(r.status_code))
                else:
                    mensaje = r.content
                    # print(locals())
                    self.agrega(mensaje)
            self.keepalive = time.time()

    def step(self):
        uid = self.lee()
        if uid:
            f.beep()
            url = URL_TARJETA.format(mac=self.mac, uid=uid, uptime=self.uptime())
            print("url = ", url, "fecha=", datetime.datetime.now())
            try:
                r = requests.get(url, timeout=5)
                if r.status_code != 200:
                    self.agrega("algo fallo", "status code: {}".format(r.status_code))
                else:
                    mensaje = r.content
                    print("respuesta =", mensaje)
                    self.agrega(mensaje)
            except requests.exceptions.ConnectTimeout:
                self.agrega("No se pudo conectar", "al servidor")
            except requests.exceptions.ConnectionError as e:
                self.agrega(str(e))
            self.keepalive = time.time()
        if len(self.lineas):
            self.muestra()
        if len(self.lineas) > self.numero_lineas:
            self.encendido = time.time()
            self.lineas.pop(0)
        self.do_keepalive()
        if self.encendido and time.time() - self.encendido > 5:
            self.borra()


if __name__ == "__main__":
    f = Fichador()
    continue_reading = True

    # Capture SIGINT for cleanup when the script is aborted
    def end_read(signal, frame):
        global continue_reading
        print("Ctrl+C captured, ending read.")
        continue_reading = False
        f.borra()
        GPIO.cleanup()

    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

    f.beep()
    f.agrega("Control horario", "kreitek")
    f.muestra()
    time.sleep(1)  # tiempo para leer
    f.borra()
    print("Press Ctrl-C to stop.")
    while continue_reading:
        f.step()
        time.sleep(1)
