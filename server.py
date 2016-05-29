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
from lcdsrv import lcd
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
deviceLocked = False

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
    global device, deviceLocked
    print 'OK ', cmd[0], cmd[1]
    if cmd[0] == 'setline':
        line = int(cmd[1][0])
        text = cmd[1][1]
        if text == "{time}":
            text = strftime("        %H:%M:%S", gmtime())
        print "printing: ", text, " in line ", line
        while deviceLocked:
            pass
        deviceLocked = True
        device.lcd_puts(text,line)
        deviceLocked = False

    elif cmd[0] == 'clearline':
        line = cmd[1][0]
        while deviceLocked:
            pass
        deviceLocked = True
        device.lcd_puts("                 ",line)
        deviceLocked = False

    elif cmd[0] == 'clear':
        while deviceLocked:
            pass
        deviceLocked = True
        device.lcd_clear()
        deviceLocked = False

def init():
    global device
    device = lcd(0x27, 1, True, False)
    ## device = lcd(0x27, 1, backlight, initFlag)
    device.lcd_clear()

init()
clockAnimation().start()
while 1:
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
