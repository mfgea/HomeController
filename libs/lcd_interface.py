import re
from threading import Thread
from time import strftime, gmtime

class lcd_interface():
    def __init__(self, address, mock=False):
        if(mock):
            from i2c_lcd_driver_mock import i2c_lcd
        else:
            from i2c_lcd_driver import i2c_lcd
        self.__device = i2c_lcd(address)
        self.screensaver = None
        self.clear()

    def set_screensaver(self, Screensaver):
        self.screensaver = Thread(target=Screensaver, args=(self,))
        self.screensaver.setDaemon(True)

    def clear(self):
        self.__device.clear()

    def load_custom_chars(self, data):
        self.__device.load_custom_chars(data)

    def backlight(self, status):
        self.__device.backlight(status)

    def display_string(self, text, line=1, pos=0):
        text = text.replace("{time}", strftime( unichr(2) + "%H:%M:%S", gmtime()))
        self.__device.display_string(text, line, pos)

    def startScreensaver(self):
        if(self.screensaver):
            self.screensaver.start()

    def stopScreensaver(self):
        if(self.screensaver):
            self.screensaver.stop()

    def parseCommand(self, data):
        validCommands = {
            'clear': r'clear',
            'clearline': r'clearline ([12])',
            'setline': r'setline ([12]) (.*)',
            'setchar': r'setchar ([12]) ([1-9]{1,2}) ([a-z])',
            'backlight': r'backlight ([01])',
            'screensaver': 'screensaver ([01])',
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

        if command:
            if command != 'quit':
                self.sendCommand(command, args)
            return { 'command': command, 'args': args }
        else:
            return False

    def sendCommand(self, cmd, args):
        global device

        if cmd == 'setline':
            line = int(args[0])
            text = args[1]
            if text == "{test}":
                text = unichr(0)+unichr(1)+unichr(2)+unichr(3)+unichr(4)+unichr(5)+unichr(6)+unichr(7)
            print "printing: ", text, " in line ", line
            self.display_string(text,line)

        elif cmd == 'setchar':
            line = int(args[0])
            pos = int(args[1])
            text = args[2]
            self.display_string(text,line,pos)

        elif cmd == 'clearline':
            line = args[0]
            self.display_string("                 ",line)

        elif cmd == 'backlight':
            status = int(args[0])
            self.backlight(status)

        elif cmd == 'screensaver':
            status = int(args[0])
            if status:
                self.startScreensaver()
            else:
                self.stopScreensaver()

        elif cmd == 'clear':
            self.clear()

        return 'OK: ', cmd, args
