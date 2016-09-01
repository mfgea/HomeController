from threading import Thread
from time import sleep
from oled.device import ssd1306, const
from oled.render import canvas
from PIL import ImageDraw, Image

class Screensaver():
    def __init__(self, device):
        self.device = device
        self.run_loop()

    def run_loop(self):
        self.running = True
        with canvas(self.device) as draw:
            logo = Image.open('images/batman.png')
            draw.bitmap((0, 0), logo=logo, fill=1)
            
        while self.running:
            sleep(500)

    def stop(self):
        self.running = False;
