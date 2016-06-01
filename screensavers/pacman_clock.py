from threading import Thread
from time import sleep

class Screensaver():
    def __init__(self, lcd):
        self.lcd = lcd
        self.run_loop()

    def run_loop(self):
        pos = 0
        prevPos = -1
        while True:
            if prevPos > -1:
                self.lcd.sendCommand('setchar', [1, prevPos, " "])
            self.lcd.sendCommand('setchar', [1, pos, unichr(5+(pos%2))])
            self.lcd.sendCommand('setchar', [1, pos+1, " "])
            self.lcd.sendCommand('setchar', [1, pos+2, unichr(7)])
            prevPos = pos
            pos = pos + 1
            if pos > 15:
                pos = 0
            self.lcd.sendCommand('setline', [2, '{time}'])
            sleep(1)


