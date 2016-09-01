#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Server for controlling output to an I2C LCD and input from a rotary encoder

Commands for LCD
CLEAR
CLEARLINE <linenumber>
SETLINE <linenumber> <text>
SETCHAR <linenumber> <pos> <char>
QUIT
"""
import socket
import sys
import argparse
import logging
import time

from gaugette.rotary_encoder import RotaryEncoder
from threading import Thread
from libs.lcd_interface_ssd1306 import lcd_interface
from libs.sensor_ds1822 import Sensors
from libs.heating_system import HeatingSystem
from libs.toggle_switch import ToggleSwitch
from screensavers.image_screensaver import Screensaver
from data import custom_characters

HOST = '127.0.0.1'
PORT = 5055
BACKLOG = 3
SIZE = 1024

##LCD_ADDRESS = 0x27
LCD_ADDRESS = 0x3C
SWITCH_PIN = 11
ENCODER_PIN_A = 10
ENCODER_PIN_B = 9

TEMP_SENSOR_PIN = 4

HEATING_LED_PIN = 25
BOILER_LED_PIN = 8

HEATING_RELAY_PIN = 23
BOILER_RELAY_PIN = 24

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#s.bind((HOST,PORT))
#s.listen(BACKLOG)

lcd = None
toggle_switch = None
encoder = None
sensors = None
heating = None
standby = True

def init(mock=False):
    global lcd, toggle_switch, encoder, sensors, heating

    lcd = lcd_interface(LCD_ADDRESS, mock)
    lcd.load_custom_chars(custom_characters.get_data())
    lcd.set_screensaver(Screensaver)
    toggle_switch = ToggleSwitch(SWITCH_PIN)
    heating = HeatingSystem(HEATING_RELAY_PIN, BOILER_RELAY_PIN, HEATING_LED_PIN, BOILER_LED_PIN)
    encoder = RotaryEncoder.Worker(ENCODER_PIN_A, ENCODER_PIN_B)
    encoder.start()

    sensors = Sensors.Worker()
    sensors.start()


sensors_data = {
    'temp': 0.0,
    'desired': 21.0,
    'humidity': 0.0,
    'standby': True
}

def clip_int(num, lower, upper):
    return max(lower, min(num, upper))

def main(args):
    init(args.mock)
    desired = sensors_data['desired']
    backlight_time = None
    last_state = False
    dirty = True
    while True:
        try:
            if not sensors_data['standby']:
                delta = encoder.get_delta()
                if delta != 0:
                    desired += 0.5 * delta
                    sensors_data['desired'] = clip_int(desired, 17, 30)
                    dirty = True

            sw_state = toggle_switch.get_state()
            if sw_state != sensors_data['standby']:
                sensors_data['standby'] = sw_state
                dirty = True

            sensors_data['temp'] = sensors.get_temperature()
            sensors_data['humidity'] = sensors.get_humidity()

            if dirty:
                backlight_time = time.time()
                lcd.backlight(1)
            elif backlight_time and time.time() - backlight_time > 10:
                backlight_time = None
                lcd.backlight(0)
               
            if dirty:
                ## Update heating system
                if sensors_data['standby']:
                    heating.system(0)
                    heating.boiler(0)
                else:
                    heating.system(1)
                    if sensors_data['desired'] > sensors_data['temp']:
                        heating.boiler(1)
                    else:
                        heating.boiler(0)

                ## Update LCD
                line1  = unichr(1) + " " + "{:.1f}%".format(sensors_data['humidity'])
                line1 += "  "
                line1 += unichr(0) + " " + "{:.1f}".format(sensors_data['temp']) + unichr(0b11011111)
                if sensors_data['standby']:
                    line2 = '       {time}'
                else:
                    line2 = unichr(4) + "   Target: " + "{:.1f}".format(sensors_data['desired']) + unichr(0b11011111)
                lcd.display_string(line1, 1)
                lcd.display_string(line2, 2)

                dirty = False

            time.sleep(.2)

        except KeyboardInterrupt:
            lcd.backlight(0)
            print "GoodBye!"
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mock', help='Uses a mock class for the lcd display (does not need a physical display)', action="store_true")
    args = parser.parse_args()
    main(args)

