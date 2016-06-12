#!/usr/bin/env python3
# coding: utf-8

from setuptools import find_packages
from distutils.core import setup

setup(name='c_locc',
      version='0.1.0.dev',
      author='XenGi',
      author_email='xen@c-base.org',
      #packages=['c_locc', 'c_locc.test'],
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      scripts=['bin/c_locc', ],
      url='https://github.com/c-base/raspberrylock',
      license='LICENSE',
      description='c-base c_locc control software',
      long_description=open('README.md').read(),
      #install_requires=['Package >= 1.0'],
	  classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Home Automation',
          'Topic :: Security',
      ],
      keywords='c-base c-lab c_locc raspberrypi',
)

