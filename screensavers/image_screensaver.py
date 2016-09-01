import os
from threading import Thread
from time import sleep
from oled.device import ssd1306, const
from oled.render import canvas
from PIL import ImageDraw, Image

class Screensaver():
    def __init__(self, interface, device):
        self.device = device
        self.run_loop()

    def run_loop(self):
        self.running = True
        dirname = os.path.dirname(os.path.realpath(__file__))
        image = dirname + '/images/cars-logo.png'
        with canvas(self.device) as draw:
            logo = Image.open(image)
            draw.bitmap((0, 0), logo, fill=1)
            
        #while self.running:
        #    sleep(500)

    def stop(self):
        self.running = False;
