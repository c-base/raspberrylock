# coding: utf-8

import logging

from pinpad import PinPad
from ldap import Ldap


class States:
    def __init__(self):
        self.logger = logging.getLogger('starting state machine..')

        self.pinpad = PinPad()
        self.ldap = Ldap()

        self.permopen = False
        self.uid = ''
        self.pwd = ''

    def state_reset(self):
        self.logger.info('entering reset state')

        self.uid = ''
        self.pwd = ''

        self.state_uid_entry()

    def state_uid_entry(self):
        self.logger.info('entering reset state')
        
        uid = ''

        while len(uid) != 4:
            key = self.pinpad.get_key()

            if key in range(9):
                uid += key
            elif key == 'A':
                if len(uid) < 4:
                    self.state_fail()
                else:
                    self.state_pin_entry()
            elif key == 'B':
                self.state_fail()
            elif key == 'C':
                self.state_fail()
            elif key == 'D':
                pass
            elif key == 'E':
                pass
            elif key == 'F':
                pass
            elif key == 'KNOB':
                if self.permopen:
                    if uid == '2342':
                        self.easteregg()
                    self.state_success()
            else:
                pass

    def state_pin_entry(self):
        pin = ''

        while True:
            key = self.pinpad.get_key()

            if key in range(9):
                pin += key
            elif key == 'A':
                if len(pin) >= 4 and self.ldap.check_credentials(self.uid, self.pin):
                    self.state_success()
                else:
                    self.state_fail()
            elif key == 'B':
                if len(pin) >= 4 and self.ldap.check_credentials(self.uid, self.pin):
                    self.permopen = None
                    self.state_success()
                else:
                    self.state_fail()
            elif key == 'C':
                self.state_fail()
            elif key == 'D':
                pass
            elif key == 'E':
                pass
            elif key == 'F':
                pass
            elif key == 'KNOB':
                if self.permopen:
                    self.state_success()
            else:
                pass

    def state_success(self):
        # TODO: open door
        if self.permopen == None:
            self.pinpad.knob_on()
            self.permopen = True

        self.state_reset()

    def state_fail(self):
        # TODO: play fail sound
        self.pinpad.knob_off()
        self.permopen = False

        self.state_reset()

    def easteregg(self):
        pass
