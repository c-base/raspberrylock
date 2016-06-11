# coding: utf-8

import logging

from RPi import GPIO


class PinPad:
    def __init__(self):
        self.logger = logging.getLogger('starting pinpad interface..')

        self.open_pin = 15
        self.rows = [11, 7, 5, 3]
        self.cols = [16, 12, 10, 8]

    def init_gpios(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.open_pin, GPIO.OUT)
        GPIO.output(self.open_pin, 0)
        for pin in self.rows:
            GPIO.setup(pin, GPIO.OUT)
        for pin in self.cols:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def get_key(self):
        return '0'

    def knob_on(self):
        pass

    def knob_off(self):
        pass
