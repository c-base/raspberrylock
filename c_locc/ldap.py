# coding: utf-8

import logging


class Ldap:
    def __init__(self):
        self.logger = logging.getLogger('starting ldap interface..')

    def check_credentials(self, uid, pin):
        return False