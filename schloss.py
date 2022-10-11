#!/usr/bin/env python3

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

import asyncio
import sys
import os
import time
import random
import subprocess

import uvloop
import gpiozero
from docopt import docopt
from loguru import logger
from ldap_interface import authenticate

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


__version__ = '2.0.0'


# GPIO.setwarnings(False)

NUMERIC_KEYS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

BOUNCE_TIME = 300  # in milliseconds
STALE_TIMEOUT = 30  # in seconds
timeouts = {'1': BOUNCE_TIME, '2': BOUNCE_TIME, '3': BOUNCE_TIME, '4': BOUNCE_TIME,
            '5': BOUNCE_TIME, '6': BOUNCE_TIME, '7': BOUNCE_TIME, '8': BOUNCE_TIME,
            '9': BOUNCE_TIME, '0': BOUNCE_TIME, 'A': BOUNCE_TIME, 'B': BOUNCE_TIME,
            'C': BOUNCE_TIME, 'D': BOUNCE_TIME, 'E': BOUNCE_TIME, 'F': BOUNCE_TIME}

Q = asyncio.queues.Queue()
# LOCK = RLock()

# ROWS and COLS for keyboard at HW lager
# ROWS = [24, 3, 5, 7]
# COLS = [15, 13, 11, 22]
# OPEN_PIN = 26

# Default ROWS, COLS and OPEN_PIN for all others
ROWS = [11, 7, 5, 3]
COLS = [16, 12, 10, 8]
OPEN_PIN = 15

door_opener = None   # initialized by init_gpios()
keyboard_rows = []
keyboard_cols = []

PLAYER = 'play'

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
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setup(OPEN_PIN, GPIO.OUT)
    door_opener = gpiozero.LED(OPEN_PIN,)
    door_opener.off()

    for pin in ROWS:
        out_pin = gpiozero.DigitalOutputDevice(pin, )
        keyboard_rows.append(out_pin)
    for pin in COLS:
        in_pin = gpiozero.DigitalInputDevice(pin, pull_up=False)
        keyboard_cols.append(in_pin)


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
    for y_pin in keyboard_rows:
        y_pin.on()
        x_pin_states = []
        for x_pin in COLS:
            pin_in = x_pin.value()
            # print("{}x{} = {}".format(y_pin, x_pin, pin_in))
            x_pin_states.append(pin_in)
        y_pin.off()
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

    logger.info("reset state")
    STATE = 0
    UID = ''
    PIN = ''


async def timeout_reset_state():
    global RESET_TIMER

    while True:
        RESET_TIMER -= 1
        if RESET_TIMER <= 0:
            reset_state()
            RESET_TIMER = STALE_TIMEOUT
        await asyncio.sleep(1.0)


async def control_loop():
    global RESET_TIMER
    global STATE, UID, PIN

    reset_state()

    # Main state machine.
    # Expects the user to enter her UID, then PIN like this:
    # [A] 2903 [A] 123456 A
    # The first and second 'A' presses are optional and ignored for compatibility with the replicator.
    # The second 'A' would be mandatory for a non-4-digit UID, luckily all c-base UIDs are 4-digit, though.
    while True:
        key = await Q.get()
        logger.info('state={}, got symbol {}'.format(STATE, '#'))
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
                loop = asyncio.get_running_loop()
                # Start the LDAP check
                open_if_correct(UID, PIN)
                reset_state()
                continue


def open_if_correct(uid, pin):
    """
    BLOCKING! Maybe this function needs to run in an executor thread.
    """
    logger.info('checking ldap ...')
    if authenticate(uid, pin):
        subprocess.Popen([PLAYER, './themes/%s/success.wav' % THEME],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        next_theme()
        door_opener.on()
        time.sleep(1)
        door_opener.off()
        time.sleep(8)

    else:
        subprocess.Popen([PLAYER, './themes/%s/fail.wav' % THEME],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)


async def keypad_loop():
    loop = asyncio.get_running_loop()
    while loop.is_running:
        key = read_keypad()
        if key:
            Q.put(key)


def main():
    loop = asyncio.new_event_loop()
    # os.nice(10)
    init_gpios()
    control_thread = loop.create_task(control_loop())
    keypad_thread =  loop.create_task(keypad_loop())
    timeout_thread = loop.create_task(timeout_reset_state())
    loop.run_forever()

if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    try:
        THEME = args['--theme']
        main()
    except KeyboardInterrupt:
        logger.info('Quitting')
        