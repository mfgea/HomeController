import re, os
from threading import Thread
from oled.device import ssd1306, const
from oled.render import canvas
from time import strftime, localtime
from PIL import ImageFont, Image

class lcd_interface():
    def __init__(self, address, mock=False):
        self.__device = ssd1306(port=1, address=0x3C)
        self.__canvas = canvas(self.__device)
        full_path = os.path.realpath(__file__)
        dirname = os.path.dirname(full_path)
        self.__font = ImageFont.truetype(dirname + '/../fonts/onesize.ttf', 14)
        self.screensaver = None
        self.clear()

    def render(self, data):
        self.__saved_data = data
        ## Update LCD
        humidity  = "{:.1f}%".format(data['humidity'])
        temperature = "{:.1f}'".format(data['temp'])
        time = '{time}'
        desired = "Target: "
        if data['standby']:
             desired = desired + "OFF"
        else:
             desired = desired + "{:.1f}'".format(data['desired'])

        temp_icon_cmap = [
            0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
            0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
            0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 0, 1, 0, 0,
            0, 1, 1, 0, 1, 1, 0, 1, 1, 0,
            1, 1, 0, 1, 1, 1, 1, 0, 1, 1,
            1, 1, 0, 1, 1, 1, 1, 0, 1, 1,
            0, 1, 1, 0, 1, 1, 0, 1, 1, 0,
            0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1, 0, 0
        ]
        hum_icon_cmap = [
            0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1, 0, 0,
            0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
            0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
            0, 1, 1, 0, 0, 0, 0, 1, 1, 0,
            1, 1, 1, 0, 0, 0, 0, 1, 1, 1,
            1, 1, 1, 0, 0, 0, 0, 1, 1, 1,
            1, 1, 0, 0, 0, 0, 0, 0, 1, 1,
            1, 1, 0, 0, 0, 0, 0, 0, 1, 1,
            1, 1, 0, 0, 0, 0, 0, 0, 1, 1,
            1, 1, 0, 0, 0, 0, 0, 0, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 0, 1, 1, 1, 1, 1, 1, 0, 0
        ]
        time_icon_cmap = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 1, 0, 1, 0, 1, 1, 0, 0,
            0, 1, 0, 0, 1, 0, 0, 1, 0, 0,
            1, 0, 0, 0, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 1, 1, 0, 1, 0,
            1, 0, 0, 0, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
            0, 1, 1, 0, 0, 0, 1, 1, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        temp_icon = Image.new('1', (10, 16), color=0)
        temp_icon.putdata(temp_icon_cmap)
        hum_icon = Image.new('1', (10, 16), color=0)
        hum_icon.putdata(hum_icon_cmap)
        time_icon = Image.new('1', (10, 16), color=0)
        time_icon.putdata(time_icon_cmap)
        time = strftime("%H:%M", localtime())
        with canvas(self.__device) as draw:
            draw.bitmap((0, 0), hum_icon, fill=255)
            draw.text((11, 0), humidity, font=self.__font, fill=255)
            draw.bitmap((64, 0), temp_icon, fill=255)
            draw.text((75, 0), temperature, font=self.__font, fill=255) 

            draw.text((0, 32), desired, font=self.__font, fill=255) 
            draw.bitmap((0, 48), time_icon, fill=255)
            draw.text((12, 48), time, font=self.__font, fill=255) 
        #self.display_string(line1, 1, 11)
        #self.display_string(line2, 2)
        #self.display_string(desired, 3)
        #self.display_string(time, 4)

    def set_screensaver(self, Screensaver):
        self.__Screensaver = Screensaver
        self.stopScreensaver()

    def clear(self):
        self.__canvas = canvas(self.__device)
        with self.__canvas as draw:
            draw.rectangle((0, 0, self.__device.width-1, self.__device.height-1), outline=0, fill=0)

    def load_custom_chars(self, data):
        #self.__device.load_custom_chars(data)
        pass

    def backlight(self, status):
        if status == 0:
            self.startScreensaver()
            #self.__device.command(const.DISPLAYOFF)
        else:
            #self.__device.command(const.DISPLAYON)
            self.stopScreensaver()
            self.render(self.__saved_data)

    def display_string(self, text, line=1, pos=0):
        text = text.replace("{time}", strftime( "%H:%M:%S", localtime()))
        y = (line - 1) * 16
        with self.__canvas as draw:
            #draw.rectangle((pos, y, self.__device.width-pos, y+16), outline=0, fill=0)
            draw.text((pos, y), text, font=self.__font, fill=255)

    def startScreensaver(self):
        print self.screensaver
        if(self.screensaver):
            self.screensaver.start()

    def stopScreensaver(self):
        if(self.__Screensaver):
            self.screensaver = Thread(target=self.__Screensaver, args=(self, self.__device,))
            self.screensaver.setDaemon(True)

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
