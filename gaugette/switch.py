import RPi.GPIO as GPIO

class Switch:

    def __init__(self, pin, pullUp=True):
        self.pin = pin
        self.pullUp = pullUp
        GPIO.setmode(GPIO.BCM)
        if self.pullUp:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, self.get_state)

    def get_state(self):
        state = GPIO.input(self.pin)
        if self.pullUp:
            # If we are pulling up and switching
            # to ground, state will be 1 when the switch is open, and 0
            # when it is closed.  We invert the value here to a more
            # conventional representation of 0:open, 1:closed.
            return 1-state
        else:
            return state
