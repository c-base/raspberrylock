#!/bin/bash

# setup vars
VIRTUAL_ENV="/opt/raspberrylock_env"
INSTALL_DIR="/opt/raspberrylock"
# end setup


PATH="${VIRTUAL_ENV}/bin:$PATH"
source ${VIRTUAL_ENV}/bin/activate
while true; do
    ${VIRTUAL_ENV}/bin/python3 ${INSTALL_DIR}/schloss.py
    echo "Restarting raspberrylock.."
done