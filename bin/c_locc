#!/usr/bin/env python3
# coding: utf-8

__author__ = 'XenGi'
__copyright__ = 'Copyright 2016, c-base'
__credits__ = ['XenGi']
__license__ = 'MIT'
__version__ = '2.0.0'
__maintainer__ = 'XenGi'
__email__ = 'xen@c-base.org'
__status__ = 'Development'

"""
c_locc - c-base lock system

Usage:
  main.py (-h | --help)
  main.py --version
Options:
  -h, --help    Show this screen.
  --version     Show version.
"""

import logging

from docopt import docopt


class c_locc:
    def __init__(self):
        self.theme = 'default'

        # create logger with 'c_locc'
        self.logger = logging.getLogger('c_locc')
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('c_locc.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.info('starting c_locc software..')


if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Application %s' % __version__)
