from threading import Thread
from time import sleep

class Screensaver(Thread):
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
            sendCommand(['setline', [2, '{time}']])
            sleep(1)


