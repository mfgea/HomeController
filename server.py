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

from gaugette.rotary_encoder import RotaryEncoder
from gaugette.switch import Switch
from threading import Thread
from libs.lcd_interface import lcd_interface
from libs.sensors import Sensors
from screensavers.pacman_clock import Screensaver
from data import custom_characters
from time import gmtime, strftime, sleep

HOST = '127.0.0.1'
PORT = 5055
BACKLOG = 3
SIZE = 1024

LCD_ADDRESS = 0x27
SWITCH_PIN = 11
ENCODER_PIN_A = 10
ENCODER_PIN_B = 9

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((HOST,PORT))
s.listen(BACKLOG)

lcd = None
switch = None
encoder = None
sensors = None

def init(mock=False):
    global lcd, switch, encoder, sensors

    lcd = lcd_interface(LCD_ADDRESS, mock)
    lcd.load_custom_chars(custom_characters.get_data())
    lcd.set_screensaver(Screensaver)
    switch = Switch(SWITCH_PIN)
    encoder = RotaryEncoder.Worker(ENCODER_PIN_A, ENCODER_PIN_B)
    encoder.start()

    sensors = Sensors.Worker()
    sensors.start()


sensors_data = {
    'temp': 0.0,
    'desired': 0.0,
    'humidity': 0.0,
    'standby': True
}

last_state = False

def main_loop():
    while True:
        delta = encoder.get_delta()
        if delta != 0:
            sensors_data['desired'] = sensors_data['desired'] + 0.5 * delta

        sw_state = switch.get_state()
        if sw_state != last_state:
            sensors_data['standby'] = not sensors_data['standby']
            last_state = sw_state

        sensors_data['temp'] = sensors.get_temperature()
        sensors_data['humidity'] = sensors.get_humidity()

        line1 = unichr(1) + " " + "{:.1%}".format(sensors_data['humidity']) + "  " + unichr(0) + " " + "{:.1f}".format(sensors_data['temp']) + "o"
        line2 = unichr(0) + " Desired: " + "{:.1f}".format(sensors_data['desired']) + "o"
        lcd.display_string(line1, 1)
        lcd.display_string(line2, 2)

def main(args):
    init(args.mock)
    main_loop()
    """
    while 1:
        try:
            client, address = s.accept()
            data = client.recv(SIZE)
            while data or 0:
                if data:
                    parsed = lcd.parseCommand(data)
                    if parsed and 'command' in parsed and parsed['command'] == 'quit':
                        client.close()
                data = client.recv(SIZE)
            else:
                client.close()

        except (socket.error), e:
            client.close()
            print e.args, e.message

        except KeyboardInterrupt:
            lcd.backlight(0)
            print "GoodBye!"
            break

        cmd = None
    """
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mock', help='Uses a mock class for the lcd display (does not need a physical display)', action="store_true")
    args = parser.parse_args()
    main(args)

