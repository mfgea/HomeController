# -*- coding: utf-8 -*-
"""
Mock file for lcd_i2c_driver.py
"""

import codecs

class i2c_lcd:
    def __prepare_string(self, string, pos=0):
        str = string
        str = str.replace(unichr(0), '#')
        str = str.replace(unichr(1), '#')
        str = str.replace(unichr(2), '#')
        str = str.replace(unichr(3), '#')
        str = str.replace(unichr(4), '#')
        str = str.replace(unichr(5), '#')
        str = str.replace(unichr(6), '#')
        str = str.replace(unichr(7), '#')


        if pos > 0:
            str = ' ' * pos + str

        return str[:16].ljust(16, ' ')

    def __print_lcd(self):
        with codecs.open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(u'\u2554' + u'\u2550' * 18 + u'\u2557' + '\n')
            f.write(u'\u2551' + ' ' + self.lines[0] + ' ' + u'\u2551' + '\n')
            f.write(u'\u2551' + ' ' + self.lines[1] + ' ' + u'\u2551' + '\n')
            f.write(u'\u255A' + u'\u2550' * 18 + u'\u255D' + '\n')

    #initializes objects and lcd
    def __init__(self, address):
        self.output_file = 'tmp/lcd.txt';
        self.lines = []
        self.clear()

    # clear lcd and set to home
    def clear(self):
        self.lines.append(" " * 16)
        self.lines.append(" " * 16)
        self.__print_lcd()

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state): # for state, 1 = on, 0 = off
        pass

    # add custom characters (0 - 7)
    def load_custom_chars(self, fontdata):
        pass

    # define precise positioning (addition from the forum)
    def display_string(self, string, line=1, pos=0):
        self.lines[line-1] = self.__prepare_string(string, pos)
        self.__print_lcd()
