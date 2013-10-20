Installation
=============

Install the piface module with the Raspberry Pi configuration tool:
sudo raspi-config (then follow the menu to Advanced -> SPI)

sudo apt-get install python3.2 python3.2-dev build-essential
sudo apt-get install libldap-2.4-2
sudo ln -s /usr/lib/arm-linux-gnueabihf/libldap_r-2.4.so.2 /usr/lib/arm-linux-gnueabihf/libldap.so
sudo ldconfig
sudo apt-get install python3-setuptools
sudo apt-get install python3-pifacedigitalios

git clone http://git.jaseg.net/python-lmap.git
cd python-lmap
python3 setup.py develop

Now clone this repository and change into its subdirectory.

Copy config.py.sample to config.py and change the password within the file.

How To Run It
===============

python3 schloss.py

Usage
======

Press A, then enter your 4 digit UID code, then press A again. Now enter your 4-6 digit PIN code and hit A.
If the code was correct, the door will open.

Hardware-Setup
================
          +-----------------------------------------------------------------------+
          |+---------------------------------------------------------------------+|
          ||+-------------------------------------------------------------------+||
          |||+-----------------------------------------------------------------+|||
          ||||  +------+.................                                      ||||
          ||||  |      |                :                   +---------------+  ||||
          |||+---+0    |  RASPBERRY PI  :                   |    KEYPAD     |  ||||
          ||+----+1    +--------+       :                   |               |  ||||
          |+-----+2             |       :                   | 1   2   3   F |  ||||
          +------+3             |       :                   | 4   5   6   E |  ||||
                |+4             +-------+                   | 7   8   9   D |  ||||
                |+5                     |                   | A   0   B   C |  ||||
                |+6                     ^                   |               |  ||||
                |+7                     |                   |               |  ||||
                |+0V                    +                   +---++++-++++---+  ||||
                |                       |    to LEDs            |||| ||||      ||||
                |                       |      ^ ^              |||| |||+------+|||
                |        PIFACE         |   Red| |Green         |||| ||+--------+||
                |                       |      | |              |||| |+----------+|
                |                       |      | |              |||| +------------+
                | ++                  7+-------+ |              ||||
                | ||                  6+---------+              ||||
                | ||                  5+------------------------+|||
                | ||                  4+-------------------------+||
                | ||  +----+ +----+   3+--------------------------+|
                | ||  |    | |    |   2+---------------------------+
                | ||  | R0 | | R1 |   1 |
                | ||  |    | |    |   0 |
                | ++  +----+ +----+ GND |
		|   .. +++    +++  +++ :|
                +-------------||--------+	  +-------------+
			      |+------------------| DOOR OPENER |-----+ +7.5V DC
			      |			  +-------------+
			      +---------------------------------------+ - (GND)
