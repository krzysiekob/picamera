#!/bin/bash

pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
#./crontab.sh
sudo cp rc.local /etc/rc.local
sudo chmod a+x /etc/rc.local

#deactivate
