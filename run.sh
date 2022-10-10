#!/bin/bash

aplay /home/pi/raspberrylock/bootup.wav

export PATH="/root/.local/bin:$PATH"
while true; do
    /usr/bin/python3 /home/pi/raspberrylock/schloss.py --theme default
#    /usr/bin/python3 /home/pi/raspberrylock/schloss.py --theme de
    echo "Restarting raspberrylock.."
done
