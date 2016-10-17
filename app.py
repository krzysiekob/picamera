# -*- coding: utf-8 -*-

import logging
import logging.handlers
from flask import Flask
from flask_bootstrap import Bootstrap
from flask import redirect
from flask import url_for
from bp_email import bp_email
from bp_home import bp_home
from bp_photo import bp_photo
from bp_info_system import bp_info_system
from bp_gallery import bp_gallery
from bp_camera import bp_camera
from bp_cron import bp_cron
from bp_user import bp_user
from bp_logs import bp_logs
from bp_server_send_event import bp_server_send_event
from bp_flickr import bp_flickr
from lib.gmail import Gmail
from lib.photo import Photo
import gevent
from gevent.wsgi import WSGIServer
import flask.ext.login as flask_login
from lib.users import User


loggingFormatter = logging.Formatter(
    'pi camera  %(asctime)s %(levelname)s %(name)s %(message)s')
logging.basicConfig(level=logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler("logs/pi_camera.log", maxBytes=50000, backupCount=50)
# file_handler = logging.FileHandler("logs/pi_camera.log")
file_handler.setFormatter(loggingFormatter)
logging.getLogger("app").addHandler(file_handler)


app = Flask(__name__)
app.secret_key = 'asd8ya7dsmkayssadasgdkags'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
Bootstrap(app)
app.register_blueprint(bp_home)
app.register_blueprint(bp_photo)
app.register_blueprint(bp_email)
app.register_blueprint(bp_gallery)
app.register_blueprint(bp_camera)
app.register_blueprint(bp_cron)
app.register_blueprint(bp_user)
app.register_blueprint(bp_logs)
app.register_blueprint(bp_server_send_event)
app.register_blueprint(bp_flickr)
app.register_blueprint(bp_info_system)

gevent.spawn(Gmail().run)
gevent.spawn(Photo().run)
gevent.spawn(Gmail().cron)


@login_manager.user_loader
def user_loader(login):
    user = User()
    if user.get_by_login(login):
        return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('bp_user.login'))


if __name__ == "__main__":
    app.debug = True
    server = WSGIServer(("", 5000), app)
    server.serve_forever()
