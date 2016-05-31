# -*- coding: utf-8 -*-
"""
Compiled, mashed and generally mutilated 2014-2015 by Denis Pleic
Made available under GNU GENERAL PUBLIC LICENSE

# Modified Python I2C library for Raspberry Pi
# as found on http://www.recantha.co.uk/blog/?p=4849
# Joined existing 'i2c_lib.py' and 'lcddriver.py' into a single library
# added bits and pieces from various sources
# By DenisFromHR (Denis Pleic)
# 2015-02-10, ver 0.1

"""
import i2c_device
from time import sleep

# LCD Address
ADDRESS = 0x27

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class lcd:
    #initializes objects and lcd
    def __init__(self):
        self.locked = True
        self.__device = i2c_device(ADDRESS)

        self.__write(0x03)
        self.__write(0x03)
        self.__write(0x03)
        self.__write(0x02)

        self.__write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.__write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.__write(LCD_CLEARDISPLAY)
        self.__write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)
        self.locked = False


    # clocks EN to latch command
    def __strobe(self, data):
        self.__device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(.0005)
        self.__device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(.0001)

    def __write_four_bits(self, data):
        self.__device.write_cmd(data | LCD_BACKLIGHT)
        self.__strobe(data)

    # write a command to lcd
    def __write(self, cmd, mode=0):
        self.__write_four_bits(mode | (cmd & 0xF0))
        self.__write_four_bits(mode | ((cmd << 4) & 0xF0))

    # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
    # works!
    def __write_char(self, charvalue, mode=1):
        self.__write_four_bits(mode | (charvalue & 0xF0))
        self.__write_four_bits(mode | ((charvalue << 4) & 0xF0))

    # clear lcd and set to home
    def clear(self):
        while self.locked:
            pass
        self.locked = True
        self.__write(LCD_CLEARDISPLAY)
        self.__write(LCD_RETURNHOME)
        self.locked = False

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state): # for state, 1 = on, 0 = off
        while self.locked:
            pass
        self.locked = True
        if state == 1:
            self.__device.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.__device.write_cmd(LCD_NOBACKLIGHT)
        self.locked = False

    # add custom characters (0 - 7)
    def load_custom_chars(self, fontdata):
        while self.locked:
            pass
        self.locked = True
        self.__write(0x40);
        for char in fontdata:
            for line in char:
                self.__write_char(line)
        self.locked = False

    # define precise positioning (addition from the forum)
    def display_string(self, string, line=1, pos=0):
        while self.locked:
            pass
        self.locked = True
        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
        elif line == 3:
            pos_new = 0x14 + pos
        elif line == 4:
            pos_new = 0x54 + pos

        self.__write(0x80 + pos_new)

        for char in string:
            self.__write(ord(char), Rs)
        self.locked = False
