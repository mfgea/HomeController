#----------------------------------------------------------------------
# rotary_encoder.py from https://github.com/guyc/py-gaugette
# Guy Carpenter, Clearwater Software
#
# This is a class for reading quadrature rotary encoders
# like the PEC11 Series available from Adafruit:
#   http://www.adafruit.com/products/377
# The datasheet for this encoder is here:
#   http://www.adafruit.com/datasheets/pec11.pdf
#
# This library expects the common pin C to be connected
# to ground.  Pins A and B will have their pull-up resistor
# pulled high.
#
# Usage:
#
#     import gaugette.rotary_encoder
#     A_PIN = 7  # use wiring pin numbers here
#     B_PIN = 9
#     encoder = gaugette.rotary_encoder.RotaryEncoder(A_PIN, B_PIN)
#     while 1:
#       delta = encoder.delta() # returns 0,1,or -1
#       if delta!=0:
#         print delta

import Adafruit_DHT
import threading
import time

class Sensors:

    #----------------------------------------------------------------------
    # Pass the wiring pin numbers here.  See:
    #  https://projects.drogon.net/raspberry-pi/wiringpi2/pins/
    #----------------------------------------------------------------------
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 4
        self.interval = 5
        self.humidity = 0.0
        self.temperature = 0.0

    def read_data(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        self.humidity = humidity
        self.temperature = temperature

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.temperature

    class Worker(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.lock = threading.Lock()
            self.stopping = False
            self.sensors = Sensors()
            self.daemon = True
            self.interval = 5

        def run(self):
            while not self.stopping:
                with self.lock:
                    self.sensors.read_data()
                time.sleep(self.interval)

        def stop(self):
            self.stopping = True

        def get_humidity(self):
            with self.lock:
                humidity = self.sensors.get_humidity()
            return humidity

        def get_temperature(self):
            with self.lock:
                temperature = self.sensors.get_temperature()
            return temperature

