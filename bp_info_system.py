from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
import os
import time
from flask.ext.login import login_required
import socket
import datetime
import subprocess

bp_info_system= Blueprint('bp_info_system', __name__, template_folder='templates')

@bp_info_system.route("/info_system", methods=["GET"])
@login_required
def info_system():
    try:
        hostname = socket.gethostname()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = subprocess.Popen("git describe --tags", shell=True, stdout=subprocess.PIPE).stdout.read()
        return render_template("info_system.html",
                               date=date,
                               version=version,
                               hostname=hostname)
    except TemplateNotFound:
        abort(404)

