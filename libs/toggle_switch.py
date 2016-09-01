import RPi.GPIO as GPIO

class ToggleSwitch:

    def __init__(self, pin, pullUp=True):
        self.pin = pin
        self.state = False
        self.enabled = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.change_state, bouncetime=200)

    def change_state(self, param):
        if self.enabled:
            self.state = not self.state

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

