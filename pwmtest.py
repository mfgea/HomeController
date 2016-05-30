#!/usr/bin/python

# requires RPi_I2C_driver.py
import RPi_I2C_driver
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

mylcd = RPi_I2C_driver.lcd()
# test 2
mylcd.lcd_display_string("RPi I2C test", 1)
mylcd.lcd_display_string(" Custom chars", 2)

p = GPIO.PWM(18, 120)  # channel=12 frequency=50Hz
p.start(0)
p.ChangeDutyCycle(10)
time.sleep(10)
p.ChangeDutyCycle(5)
time.sleep(10)
p.stop()
GPIO.cleanup()

mylcd.lcd_clear()
mylcd.backlight(0)

"""
try:
    while 1:
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
p.stop()
GPIO.cleanup()
"""
