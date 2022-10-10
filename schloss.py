#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
c-lab schloss

Usage:
  schloss.py [--theme <theme>]
  schloss.py (-h | --help)
  schloss.py --version

Options:
  -h --help        Show this screen.
  --version        Show version.
  --theme=<theme>  Sound theme [default: default].
"""

import os
import time
import random
import subprocess
from queue import Queue
from threading import Thread, RLock

from docopt import docopt
from RPi import GPIO

from ldap_interface import authenticate


__version__ = '0.1.0'


GPIO.setwarnings(False)

NUMERIC_KEYS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

BOUNCE_TIME = 300  # in milliseconds
STALE_TIMEOUT = 30  # in seconds
timeouts = {'1': BOUNCE_TIME, '2': BOUNCE_TIME, '3': BOUNCE_TIME, '4': BOUNCE_TIME,
            '5': BOUNCE_TIME, '6': BOUNCE_TIME, '7': BOUNCE_TIME, '8': BOUNCE_TIME,
            '9': BOUNCE_TIME, '0': BOUNCE_TIME, 'A': BOUNCE_TIME, 'B': BOUNCE_TIME,
            'C': BOUNCE_TIME, 'D': BOUNCE_TIME, 'E': BOUNCE_TIME, 'F': BOUNCE_TIME}

Q = Queue()
LOCK = RLock()

# ROWS and COLS for keyboard at HW lager
# ROWS = [24, 3, 5, 7]
# COLS = [15, 13, 11, 22]
# OPEN_PIN = 26

# Default ROWS, COLS and OPEN_PIN for all others
ROWS = [11, 7, 5, 3]
COLS = [16, 12, 10, 8]
OPEN_PIN = 15


PLAYER = 'aplay'

MONGO = None

STATE = 0
UID = ''
PIN = ''
RESET_TIMER = STALE_TIMEOUT


def next_theme():
    """
    Look into themes folder and find all installed themes. Get a random one which is not the current one.
    """
    global THEME
    themes = next(os.walk('./themes/'))[1]
    OLD_THEME = THEME
    while THEME != OLD_THEME:
        THEME = random.choice(themes)


def init_gpios():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(OPEN_PIN, GPIO.OUT)
    GPIO.output(OPEN_PIN, 0)
    for pin in ROWS:
        GPIO.setup(pin, GPIO.OUT)
    for pin in COLS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def decode_keypad(measurements):
    """
    x1 = (0,0,1,0)
    """
    layout = [['C', 'D', 'E', 'F'], ['B', '9', '6', '3'],
              ['0', '8', '5', '2'], ['A', '7', '4', '1']]
    for y_index, y_row in enumerate(measurements):
        for x_index, x_state in enumerate(y_row):
            if x_state > 0:
                return layout[y_index][x_index]


def decrease_timeouts(timeouts):
    for k, v in timeouts.items():
        if v > 0:
            timeouts[k] = v - 1
    return timeouts


def collect_measurements():
    """
s    """
    pin_state = []
    for y_pin in ROWS:
        GPIO.output(y_pin, 1)
        x_pin_states = []
        for x_pin in COLS:
            pin_in = GPIO.input(x_pin)
            # print("{}x{} = {}".format(y_pin, x_pin, pin_in))
            x_pin_states.append(pin_in)
        GPIO.output(y_pin, 0)
        pin_state.append(x_pin_states)
    return pin_state


def read_keypad():
    decrease_timeouts(timeouts)
    key = decode_keypad(collect_measurements())
    if key:
        if timeouts[key] > 0:
            return None
        else:
            num = random.randint(0, 9)
            subprocess.Popen([PLAYER, './themes/%s/%s.wav' % (THEME, num)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(PLAYER, './themes/%s/%s.wav' % (THEME, num))
            timeouts[key] = BOUNCE_TIME
            return key
    else:
        return None


def reset_state():
    global STATE, UID, PIN

    print("reset state")
    STATE = 0
    UID = ''
    PIN = ''


def timeout_reset_state():
    global RESET_TIMER

    while True:
        RESET_TIMER -= 1
        if RESET_TIMER <= 0:
            reset_state()
            RESET_TIMER = STALE_TIMEOUT
        time.sleep(1.0)


def control_loop():
    global RESET_TIMER
    global STATE, UID, PIN

    reset_state()

    # Main state machine.
    # Expects the user to enter her UID, then PIN like this:
    # [A] 2903 [A] 123456 A
    # The first and second 'A' presses are optional and ignored for compatibility with the replicator.
    # The second 'A' would be mandatory for a non-4-digit UID, luckily all c-base UIDs are 4-digit, though.
    while True:
        key = Q.get()
        print('state={}, got symbol {}'.format(STATE, '#'))
        RESET_TIMER = STALE_TIMEOUT
        Q.task_done()
        if STATE == 0:
            if key == 'A':
                # print('Enter UID:')
                STATE = 0
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key in NUMERIC_KEYS:
                UID += key
                STATE = 1
                continue
        elif STATE == 1:
            if key in NUMERIC_KEYS:
                if len(UID) < 4:
                    UID += key
                    STATE = 1
                else:
                    PIN += key
                    STATE = 2
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                STATE = 2
                continue
        elif STATE == 2:
            if key in NUMERIC_KEYS:
                PIN += key
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                t = Thread(target=open_if_correct, args=(UID, PIN))
                t.start()
                reset_state()
                continue


def open_if_correct(uid, pin):
    print('checking ldap ...')
    if authenticate(uid, pin):
        subprocess.Popen([PLAYER, './themes/%s/success.wav' % THEME],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        next_theme()
        with LOCK:
            GPIO.output(OPEN_PIN, 1)
            time.sleep(1)
            GPIO.output(OPEN_PIN, 0)
            time.sleep(8)
    else:
        subprocess.Popen([PLAYER, './themes/%s/fail.wav' % THEME],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with LOCK:
            time.sleep(2)


def keypad_loop():
    while True:
        with LOCK:
            key = read_keypad()
            if key:
                Q.put(key)


def main():
    # os.nice(10)
    init_gpios()
    control_thread = Thread(target=control_loop)
    control_thread.start()
    keypad_thread = Thread(target=keypad_loop)
    keypad_thread.start()
    timeout_thread = Thread(target=timeout_reset_state)
    timeout_thread.start()


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    try:
        THEME = args['--theme']
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
