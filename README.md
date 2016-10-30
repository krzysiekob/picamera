# ReefNet

1.
apt-get install build-essential python-dev python-setuptools

apt-get install libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms1-dev libwebp-dev libjpeg-dev

pip install Flask flask-bootstrap requests flask-paginate flask-login passlib gevent Pillow

2.
/etc/rc.local

echo "Start PI Camera"

cd /home/pi/picamera; su pi -s /usr/bin/python app.py &


3.
cd /home/pi/picamera; su pi -s /usr/bin/python app.py &

