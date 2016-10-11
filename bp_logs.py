from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from flask.ext.login import login_required
import glob
import os

bp_logs = Blueprint('bp_logs', __name__, template_folder='templates')


@bp_logs.route("/logs", methods=["GET"])
@bp_logs.route("/logs/<file_name>", methods=["GET"])
@login_required
def edit(file_name=None):
    try:
        data = ''
        logfiles = [os.path.basename(log) for log in glob.glob('logs/*')]
        if file_name is not None:
            with open('logs/' + file_name, 'rt') as f:
                data = f.read()

        return render_template("logs.html",
                               logfiles=logfiles,
                               data=data
                               )

    except TemplateNotFound:
        abort(404)
