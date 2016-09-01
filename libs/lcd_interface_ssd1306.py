import re, os
from threading import Thread
from oled.device import ssd1306, const
from oled.render import canvas
from time import strftime, localtime
from PIL import ImageFont

class lcd_interface():
    def __init__(self, address, mock=False):
        self.__device = ssd1306(port=1, address=0x3C)
        self.__canvas = canvas(self.__device)
        full_path = os.path.realpath(__file__)
        dirname = os.path.dirname(full_path)
        self.__font = ImageFont.truetype(dirname + '/../fonts/onesize.ttf', 14)
        self.screensaver = None
        self.clear()

    def set_screensaver(self, Screensaver):
        self.screensaver = Thread(target=Screensaver, args=(self,))
        self.screensaver.setDaemon(True)
        pass

    def clear(self):
        self.__canvas = canvas(self.__device)
        with self.__canvas as draw:
            draw.rectangle((0, 0, self.__device.width-1, self.__device.height-1), outline=0, fill=0)

    def load_custom_chars(self, data):
        #self.__device.load_custom_chars(data)
        pass

    def backlight(self, status):
        if status == 0:
            self.__device.command(const.DISPLAYOFF)
        else:
            self.__device.command(const.DISPLAYON)

    def display_string(self, text, line=1, pos=0):
        text = text.replace("{time}", strftime( unichr(2) + "%H:%M:%S", localtime()))
        y = (line - 1) * 16
        with self.__canvas as draw:
            draw.rectangle((pos, y, self.__device.width-pos, y+16), outline=0, fill=0)
            draw.text((pos, y), text, font=self.__font, fill=255)

    def startScreensaver(self):
        if(self.screensaver):
            self.screensaver.start()
        pass

    def stopScreensaver(self):
        if(self.screensaver):
            self.screensaver.stop()
        pass

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
