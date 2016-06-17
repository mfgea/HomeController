import threading
import time
from w1thermsensor import W1ThermSensor

class Sensors:

    #----------------------------------------------------------------------
    # Pass the wiring pin numbers here.  See:
    #  https://projects.drogon.net/raspberry-pi/wiringpi2/pins/
    #----------------------------------------------------------------------
    def __init__(self):
        self.sensor = W1ThermSensor()
        self.pin = 4
        self.temperature = 0.0

    def read_data(self):
        temperature = self.sensor.get_temperature()
        if temperature:
            self.temperature = temperature

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return 0.0

    class Worker(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.lock = threading.Lock()
            self.stopping = False
            self.sensors = Sensors()
            self.daemon = True
            self.interval = 60

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


if __name__ == '__main__':
    sensors = Sensors()
    sensors.read_data()
    print sensors.get_temperature()
    print sensors.get_humidity()
