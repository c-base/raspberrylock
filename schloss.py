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
import queue
import random
import subprocess
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

q = queue.Queue()
lock = RLock()

ROWS = [11, 7, 5, 3]
COLS = [16, 12, 10, 8]


OPEN_PIN = 15

PLAYER = 'aplay'

MONGO = None

state = 0
uid = ''
pin = ''
reset_timer = STALE_TIMEOUT

def next_theme():
    global THEME
    themes = next(os.walk('/opt/raspberrylock/sounds/'))[1]
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
    """
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
            subprocess.Popen([PLAYER, '/opt/raspberrylock/sounds/%s/%s.wav' % (THEME, num)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            timeouts[key] = BOUNCE_TIME
            return key
    else:
        return None


def reset_state():
    global state, uid, pin

    print("reset state")
    state = 0
    uid = ''
    pin = ''


def timeout_reset_state():
    global reset_timer

    while True:
        reset_timer -= 1
        if reset_timer <= 0:
            reset_state()
            reset_timer = STALE_TIMEOUT
        time.sleep(1.0)


def control_loop():
    global reset_timer
    global state, uid, pin

    reset_state()

    # Main state machine.
    # Expects the user to enter her UID, then PIN like this:
    # [A] 2903 [A] 123456 A
    # The first and second 'A' presses are optional and ignored for compatibility with the replicator.
    # The second 'A' would be mandatory for a non-4-digit UID, luckily all c-base UIDs are 4-digit, though.
    while True:
        key = q.get()
        print('state={}, got symbol {}'.format(state, '#'))
        reset_timer = STALE_TIMEOUT
        q.task_done()
        if state == 0:
            if key == 'A':
                # print('Enter UID:')
                state = 0
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key in NUMERIC_KEYS:
                uid += key
                state = 1
                continue
        elif state == 1:
            if key in NUMERIC_KEYS:
                if len(uid) < 4:
                    uid += key
                    state = 1
                else:
                    pin += key
                    state = 2
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                state = 2
                continue
        elif state == 2:
            if key in NUMERIC_KEYS:
                pin += key
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                t = Thread(target=open_if_correct, args=(uid, pin))
                t.start()
                reset_state()
                continue


def open_if_correct(uid, pin):
    print('checking ldap ...')
    if authenticate(uid, pin):
        subprocess.Popen([PLAYER, '/opt/raspberrylock/sounds/%s/success.wav' % THEME],
			 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        next_theme()
        with lock:
            GPIO.output(OPEN_PIN, 1)
            time.sleep(1)
            GPIO.output(OPEN_PIN, 0)
            time.sleep(13)
    else:
        subprocess.Popen([PLAYER, '/opt/raspberrylock/sounds/%s/fail.wav' % THEME],
			 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with lock:
            time.sleep(2)


def keypad_loop():
    while True:
        with lock:
            key = read_keypad()
            if key:
                q.put(key)


def main():
    #os.nice(10)
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
        main()
        THEME = args['--theme']
    except KeyboardInterrupt:
        GPIO.cleanup()
