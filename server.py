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
import re
import socket
from lib.lcd_i2c_driver import i2c_lcd
from data import custom_characters
from time import *
from time import gmtime, strftime
from threading import Thread

host = '127.0.0.1'
port = 5055
backlog = 3
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((host,port))
s.listen(backlog)

device = None

customCharacters = [
    # Char 0: thermometer
    [
        0b00100,
        0b01010,
        0b01010,
        0b01110,
        0b01110,
        0b11111,
        0b11111,
        0b01110
    ],
    # Char 1: water drop
    [
        0b00100,
        0b00100,
        0b01010,
        0b01010,
        0b10001,
        0b10001,
        0b10001,
        0b01110
    ],
    # Char 2: clock
    [
        0b00000,
        0b01110,
        0b10101,
        0b10111,
        0b10001,
        0b01110,
        0b00000,
        0b00000
    ],
    # Char 3: arrow
    [
        0b01000,
        0b01100,
        0b11110,
        0b11111,
        0b11110,
        0b01100,
        0b01000,
        0b00000
    ],
    # Char 4: heart
    [
        0b00000,
        0b01010,
        0b11111,
        0b11111,
        0b01110,
        0b00100,
        0b00000,
        0b00000
    ],
    # Char 5: pacman open
    [
        0b00000,
        0b01111,
        0b11010,
        0b11100,
        0b11110,
        0b01111,
        0b00000,
        0b00000
    ],
    # Char 6: pacman closed
    [
        0b00000,
        0b01110,
        0b11011,
        0b11100,
        0b11111,
        0b01110,
        0b00000,
        0b00000
    ],
    # Char 7: ghost
    [
        0b00000,
        0b01110,
        0b10101,
        0b11111,
        0b11111,
        0b10101,
        0b00000,
        0b00000
    ]
];

"""
    # bell
    [
        0b00000,
        0b00100,
        0b01110,
        0b01110,
        0b01110,
        0b11111,
        0b00100,
        0b00000
    ],
    # tick
    [
        0b00000,
        0b00000,
        0b00001,
        0b00010,
        0b10100,
        0b01000,
        0b00000,
        0b00000
    ],
    # alien
    [
        0b11111,
        0b10101,
        0b11111,
        0b11111,
        0b01110
        0b01010,
        0b11011,
        0b00000,
    ],
    # pacman tall
    [
        0b01110,
        0b11011,
        0b11110,
        0b11100,
        0b11110,
        0b11111,
        0b01110,
        0b00000
    ],
    # ghost tall
    [
        0b01110,
        0b01110,
        0b11111,
        0b10101,
        0b11111,
        0b11111,
        0b10101,
        0b00000
    ],
"""

class pacmanAnimation(Thread):
    def run(self):
        pos = 0
        prevPos = -1
        while True:
            if prevPos > -1:
                sendCommand([ 'setchar', [1, prevPos, " "]])
            sendCommand([ 'setchar', [1, pos, unichr(5+(pos%2))]])
            sendCommand([ 'setchar', [1, pos+1, " "]])
            sendCommand([ 'setchar', [1, pos+2, unichr(7)]])
            prevPos = pos
            pos = pos + 1
            if pos > 15:
                pos = 0
            sleep(1)

class clockAnimation(Thread):
    def run(self):
        while True:
            sendCommand(['setline', [2, '{time}']])
            sleep(1)

def parseCommand(data):
    validCommands = {
        'clear': r'clear',
        'clearline': r'clearline ([12])',
        'setline': r'setline ([12]) (.*)',
        'setchar': r'setchar ([12]) ([1-9]{1,2}) ([a-z])',
        'backlight': r'backlight ([01])',
        'quit': r'quit'
    }

    command = None
    args = None

    data = data.rstrip()

    for i in validCommands:
        matchObj = re.match(validCommands[i], data, re.I)
        if matchObj:
            command = i
            args = matchObj.groups()

    return [ command, args ]

def sendCommand(cmd):
    global device
    print 'OK ', cmd[0], cmd[1]

    if cmd[0] == 'setline':
        line = int(cmd[1][0])
        text = cmd[1][1]
        if text == "{test}":
            text = unichr(0)+unichr(1)+unichr(2)+unichr(3)+unichr(4)+unichr(5)+unichr(6)+unichr(7)
        if text == "{time}":
            text = strftime(unichr(4) + "Ana" + unichr(4) + " " + unichr(2) + " %H:%M:%S", gmtime())
        print "printing: ", text, " in line ", line
        device.display_string(text,line)

    elif cmd[0] == 'setchar':
        line = int(cmd[1][0])
        pos = int(cmd[1][1])
        text = cmd[1][2]
        device.display_string(text,line,pos)

    elif cmd[0] == 'clearline':
        line = cmd[1][0]
        device.display_string("                 ",line)

    elif cmd[0] == 'backlight':
        status = int(cmd[1][0])
        device.backlight(0)

    elif cmd[0] == 'clear':
        device.clear()

def init():
    global device
    device = i2c_lcd(0x27, 1, backlight=True)
    device.clear()
    device.load_custom_chars(customCharacters)


init()
clockAnimation().start()
pacmanAnimation().start()
#thread = clockAnimation()
#thread.start()
while 1:
    #thread.join(500)
    #if not thread.isAlive():
    #    break
    client, address = s.accept()
    try:
        data = client.recv(size)
        while data or 0:
            if data:
                cmd = parseCommand(data)

            if cmd:
                if cmd[0] == 'quit':
                    client.close()
                else:
                    sendCommand(cmd)
            else:
                print "Invalid command"
            data = client.recv(size)
        else:
            client.close()
    except (socket.error), e:
        client.close()
        print e.args, e.message

    cmd = None
