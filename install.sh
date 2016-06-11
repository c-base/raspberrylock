#!/bin/bash

# create temporary working dir
workdir=`mktemp -d`
cd workdir

# clone the repo
git clone https://github.com/c-base/raspberrylock.git
cd raspberrylock

# copy files
cp -r c_locc /opt/
chown -R root:root /opt/c_locc/

# install dependencies
apt update
apt install python3 python-ldap

# setup systemd unit
cp c_locc.service /etc/systemd/system/
systemctl enable c_locc
systemctl start c_locc

# cleanup
cd /tmp
rm -rf $workdir
