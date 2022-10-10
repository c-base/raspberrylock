#!/usr/bin/env python3

import time
import subprocess
from RPi import GPIO

OPEN_PIN = 26

GPIO.setwarnings(False)

def main():
    subprocess.Popen(["aplay", "-q", "/home/pi/raspberrylock/themes/default/success.wav"])
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(OPEN_PIN, GPIO.OUT)
    GPIO.output(OPEN_PIN, 0)
    GPIO.output(OPEN_PIN, 1)
    time.sleep(4.0)
    GPIO.output(OPEN_PIN, 0)

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
