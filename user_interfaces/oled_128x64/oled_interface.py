import re, os
from threading import Thread
from libs.device import ssd1306, const
from libs.render import canvas
from time import strftime, localtime
from PIL import ImageFont, Image
from random import randint

from data import custom_glyphs

class output_interface():
    def __init__(self, address, mock=False):
        self.line_height = 16
        self.__saved_data = None

        self.__device = ssd1306(port=1, address=0x3C)
        self.__dirname = os.path.dirname(os.path.realpath(__file__))
        self.__font = ImageFont.truetype(self.__dirname + '/fonts/onesize.ttf', 14)

        self.custom_glyphs = custom_glyphs.get_data()

    def get_glyph(self, name):
        glyph = Image.new('1', (10, 16), color=0)
        glyph.putdata(self.custom_glyphs[name])
        return glyph

    def render(self, data):
        self.__saved_data = data

        ## Update LCD
        humidity  = "{:.1f}%".format(data['humidity'])
        temperature = "{:.1f}".format(data['temp'])
        time = strftime("%H:%M", localtime())
        desired = "Target: "
        if data['standby']:
            desired = desired + "OFF"
        else:
            desired = desired + "{:.1f}".format(data['desired'])

        with canvas(self.__device) as draw:
            draw.bitmap((0, 0), self.get_glyph('hum'), fill=255)
            draw.text((12, 0), humidity, font=self.__font, fill=255)
            draw.bitmap((64, 0), self.get_glyph('temp'), fill=255)
            draw.text((76, 0), temperature, font=self.__font, fill=255) 
            symbolpos = draw.textsize(temperature, font=self.__font)
            draw.bitmap((76+symbolpos[0],0), self.get_glyph('degrees'), fill=255)

            draw.text((0, 32), desired, font=self.__font, fill=255) 
            if not data['standby']:
                symbolpos = draw.textsize(desired, font=self.__font)
                draw.bitmap((symbolpos[0],32), self.get_glyph('degrees'), fill=255)

            textsize = draw.textsize(time, font=self.__font)
            textpos = 128 - textsize[0]
            draw.bitmap((textpos - 10, 48), self.get_glyph('time'), fill=255)
            draw.text((textpos, 48), time, font=self.__font, fill=255) 

    def turn_off(self):
        #self.__device.command(const.DISPLAYOFF)
        file_name = ['cars-logo.png', 'batman.png'][randint(0,1)]
        image = self.__dirname + '/images/' + file_name
        with canvas(self.__device) as draw:
            logo = Image.open(image)
            draw.bitmap((0, 0), logo, fill=1)

    def turn_on(self):
        if self.__saved_data:
            self.render(self.__saved_data)
        #self.__device.command(const.DISPLAYON)

