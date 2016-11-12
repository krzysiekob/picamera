#!/bin/bash

cd /home/pi/picamera
v1=`git describe --tags`
git pull
v2=`git describe --tags`
if [ "$v1" != "$v2" ]; then
    pkill -f app.py
    ./start.sh & > /dev/null
fi
