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
