c_locc
======

The c_locc software is a small application that runs on a raspberry pi. It
reads a 4-digit user-ID and a 4-8 digit passcode from a 4x4 matrix keypad. It
then sends this data to a LDAP server to check if the entered user-id and
passcode combination is correct. If the server answers with "correct", a door
is opened by switching on an electric strike with a relais.


Installation
------------

Use the tool `raspi-config` and activate SPI by going to Advanced -> SPI.

Now you can use the `install.sh` file to setup the rest:

```
curl -SsL https://raw.githubusercontent.com/c-base/raspberrylock/master/install.sh | sudo bash
```

Copy `/opt/c_locc/config.ini.sample` to `/opt/c_locc/config.ini` and change the config values to your
needs.

Usage
-----

Enter your 4 digit UID code. Now enter your 4-8 digit PIN code and hit A. If
the code was correct, the door will open. You can also hit B instead of A
and the door will stay permanently open. The next visitor can just press the
button on the door knob to enter.

Hardware-Setup
----------------

```
TODO: draw nice grafic with pins and stuff
```

Additional Links
--------------------

  - Keypad used in the project:
    http://uk.farnell.com/eao/eco-16250-06/keypad-4x4-matrix-0-02a-24v-plastic/dp/1130806
