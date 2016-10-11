# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from flask import request
from lib.settings import Settings
from flask.ext.login import login_required
from lib.gmail import Gmail

bp_email = Blueprint('bp_email', __name__, template_folder='templates')


@bp_email.route("/email", methods=["GET", "POST"])
@login_required
def edit():
    try:
        name = 'email'
        settings = Settings()
        settings_data = settings.get(name)
        form_info = ''
        if request.method == 'POST':
            user = ''
            pwd = ''            
            for option, value in request.form.items():
                if option == 'gmail_user':
                    user = value
                if option == 'gmail_pwd':
                    pwd = value
            
            gmail = Gmail()
            check_connect = gmail.check_connect(user, pwd)
            
            if check_connect is True and settings.set_form(form=request.form,
                                                           section_name=name) is True and settings.set_params(section_name='email', option='gmail_is_connect', value='1') is True:
                form_info = "OK"
                settings_data = settings.get(name)
            else:
                form_info = "ERROR"
        else:
            gmail = Gmail()
            check_connect = gmail.check_connect()
            
        return render_template("email.html",
                               form=settings_data,
                               form_info=form_info,
                               check_connect=check_connect)

    except TemplateNotFound:
        abort(404)
