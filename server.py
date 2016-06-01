#!/usr/bin/env python

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
from threading import Thread
from libs.lcd_interface import lcd_interface
from screensavers.pacman_clock import Screensaver
from data import custom_characters
from time import gmtime, strftime, sleep

ADDRESS = 0x27
HOST = '127.0.0.1'
PORT = 5055
BACKLOG = 3
SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((HOST,PORT))
s.listen(BACKLOG)

lcd = None

def init(mock=False):
    global lcd
    lcd = lcd_interface(ADDRESS, mock)
    lcd.load_custom_chars(custom_characters.get_data())
    lcd.set_screensaver(Screensaver)

def main(args):
    init(args.mock)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mock', help='Uses a mock class for the lcd display (does not need a physical display)', action="store_true")
    args = parser.parse_args()
    main(args)

