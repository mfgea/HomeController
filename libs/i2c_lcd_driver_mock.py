# -*- coding: utf-8 -*-
"""
Mock file for lcd_i2c_driver.py
"""

class i2c_lcd:
    #initializes objects and lcd
    def __init__(self):
        print "Initialized!"

    # clear lcd and set to home
    def clear(self):
        print "Cleared!"

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state): # for state, 1 = on, 0 = off
        print "Backlight: ", state

    # add custom characters (0 - 7)
    def load_custom_chars(self, fontdata):
        print "Charset loaded"

    # define precise positioning (addition from the forum)
    def display_string(self, string, line=1, pos=0):
        print "Display String at ", line, pos, ":", string
