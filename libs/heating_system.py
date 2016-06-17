import threading
import RPi.GPIO as GPIO
import time

class HeatingSystem:

    #----------------------------------------------------------------------
    # Pass the wiring pin numbers here.  See:
    #  https://projects.drogon.net/raspberry-pi/wiringpi2/pins/
    #----------------------------------------------------------------------
    def __init__(self, system_relay_pin, boiler_relay_pin, system_led_pin, boiler_led_pin):
        self.boiler_status = 0
        self.system_status = 0
        self.system_relay_pin = system_relay_pin
        self.boiler_relay_pin = boiler_relay_pin
        self.system_led_pin = system_led_pin
        self.boiler_led_pin = boiler_led_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(system_relay_pin, GPIO.OUT)
        GPIO.setup(boiler_relay_pin, GPIO.OUT)
        GPIO.setup(system_led_pin, GPIO.OUT)
        GPIO.setup(boiler_led_pin, GPIO.OUT)

    def system(self, status):
        self.system_status = status
        GPIO.output(self.system_led_pin, status)
        GPIO.output(self.system_relay_pin, status)

    def boiler(self, status):
        self.boiler_status = status
        GPIO.output(self.boiler_led_pin, status)
        GPIO.output(self.boiler_relay_pin, status)

    class Worker(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.lock = threading.Lock()
            self.stopping = False
            self.heating_system = HeatingSystem()
            self.daemon = True
            self.interval = 0.1

        def run(self):
            while not self.stopping:
                time.sleep(self.interval)

        def stop(self):
            self.stopping = True

        def boiler(self, status):
            with self.lock:
                self.heating_system.boiler(status)

        def system(self, status):
            with self.lock:
                self.heating_system.system(status)

if __name__ == '__main__':
    heating_system = HeatingSystem(17, 22)
    heating_system.system(1)
    time.sleep(2)
    heating_system.boiler(1)
    time.sleep(2)
    heating_system.system(0)
    time.sleep(2)
    heating_system.boiler(0)
    time.sleep(2)
