import I2C_LCD_driver
from time import sleep


mylcd = I2C_LCD_driver.lcd()
mylcd.backlight(1)
linea_blanca = " " * 16



mensaje = "This is a string that needs to scroll"


mylcd.lcd_display_string(mensaje[:16])
sleep(2)  # tiempo para leer
mylcd.lcd_display_string(linea_blanca, 1)
mylcd.backlight(0)
