#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
# import pifacedigitalio as pfio
import queue
from threading import Thread, RLock

from ldap_interface import authenticate

NUMERIC_KEYS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

timeouts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0,
            '9': 0, '0': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}

q = queue.Queue()
lock = RLock()

# for piface
# ROWS = [2, 3, 4, 5]
# COLS = [0, 1, 2, 3]

ROWS = [2, 3, 4, 5]
COLS = [0, 1, 2, 3]

def init_piface():
    pfio.init()
    pfio.digital_write_pullup(0, 1)
    pfio.digital_write_pullup(1, 1)
    pfio.digital_write_pullup(2, 1)
    pfio.digital_write_pullup(3, 1)
    
def init_gpios():
    GPIO.setmode(GPIO.BOARD)
    for pin in ROWS:
        GPIO.setup(pin, GPIO.OUT)
    for pin in COLS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
        pfio.digital_write(y_pin, 1)
        x_pin_states = []
        for x_pin in :
            pin_in = pfio.digital_read(x_pin)
            x_pin_states.append(pin_in)
        pfio.digital_write(y_pin, 0)
        pin_state.append(x_pin_states)
    return pin_state

def read_keypad():
    decrease_timeouts(timeouts)
    key = decode_keypad(collect_measurements())
    if key:
        if timeouts[key] > 0:
            return None
        else:
            timeouts[key] = 10
            return key
    else:
        return None

def control_loop():
    state = 0
    uid = '' 
    pin = ''
    # Main state machine.
    # Expects the user to enter her UID, then PIN like this:
    # [A] 2903 [A] 123456 A
    # The first and second 'A' presses are optional and ignored for compatibility with the replicator.
    # The second 'A' would be mandatory for a non-4-digit UID, luckily all c-base UIDs are 4-digit, though.
    while True:
        key = q.get()
        q.task_done()
        if state == 0:
            if key == 'A':
                # print('Enter UID:')
                state = 1
                continue
            elif key == 'C':
                state = 0
                uid = ''
                pin = ''
                continue
        if state == 0:
            if key in NUMERIC_KEYS:
                if len(uid) < 4:
                    uid += key
                # ignore if longer
                continue
            if key == 'C':
                state = 0
                uid = ''
                pin = ''
                continue
            if key == 'A':
                if len(uid) == 4:
                    state = 2
                    # print('Enter PIN:')
                    continue
        elif state == 1:
            if key in NUMERIC_KEYS:
                pin += key
            elif key == 'A' and len(pin) > 0:
                t = Thread(target=open_if_correct, args=(uid, pin))
                t.start()
                state = 0
                uid = ''
                pin = ''

def open_if_correct(uid, pin):
    print('checking ldap ...')
    if authenticate(uid, pin):
        with lock:
            pfio.digital_write(6, 1)
            pfio.digital_write(1, 1)
            time.sleep(10)
            pfio.digital_write(6, 0)
            pfio.digital_write(1, 0)
    else:
        with lock:
            pfio.digital_write(7, 1)
            time.sleep(2)
            pfio.digital_write(7, 0)

def keypad_loop():
    while True:
        with lock:
            key = read_keypad()
            if key:
                q.put(key)

def main():
    # pfio.init()
    init_gpios()
    control_thread = Thread(target=control_loop)
    control_thread.start()
    keypad_thread = Thread(target=keypad_loop)
    keypad_thread.start()

if __name__ == '__main__':
    main()
