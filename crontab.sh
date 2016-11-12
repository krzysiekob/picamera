#!/bin/bash

echo "*/10 * * * * /bin/bash /home/pi/picamera/update.sh > /dev/null 2>&1" >> mycron
echo "*/1 * * * * /home/pi/picamera/reconnect.sh >> /dev/null" >> mycron
crontab mycron
rm mycron
