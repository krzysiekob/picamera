# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from flask import request
from lib.settings import Settings
from flask.ext.login import login_required

bp_cron = Blueprint('bp_cron', __name__, template_folder='templates')


@bp_cron.route("/cron", methods=["GET", "POST"])
@login_required
def edit():
    try:
        name = 'cron'
        settings = Settings()
        settings_data = settings.get(name)
        form_info = ''
        if request.method == 'POST':
            if settings.set_form(form=request.form,
                                 section_name=name) is True:
                form_info = "OK"
                settings_data = settings.get(name)
            else:
                form_info = "ERROR"
        return render_template("cron.html",
                               form=settings_data,
                               form_info=form_info, settings_email=settings.get('email'))

    except TemplateNotFound:
        abort(404)
