# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from flask import request
from lib.settings import Settings
from flask.ext.login import login_required
from lib.flickr import Flickr

bp_flickr = Blueprint('bp_flickr', __name__, template_folder='templates')


@bp_flickr.route("/flickr/edit", methods=["GET", "POST"])
@login_required
def edit():
    try:
        name = 'flickr'
        settings = Settings()
        settings_data = settings.get(name)
        form_info = ''

        flickr = Flickr()
        checkToken = flickr.checkToken();
        
        if request.method == 'POST':
            if settings.set_form(form=request.form,
                                 section_name=name) is True:
                form_info = "OK"
                settings_data = settings.get(name)
            else:
                form_info = "ERROR"
        return render_template("flickr.html",
                               form=settings_data,
                               form_info=form_info, checkToken=checkToken)

    except TemplateNotFound:
        abort(404)


@bp_flickr.route("/flickr/api", methods=["GET", "POST"])
@login_required
def api():
    try:
        name = 'flickr'
        settings = Settings()
        settings_data = settings.get(name)
        form_info = ''
        back = {'frob': '', 'url': ''}

        flickr = Flickr()
        checkToken = flickr.checkToken();
                            
        if request.method == 'POST':
            if settings.set_form(form=request.form,
                                 section_name=name) is True:                
                form_info = "OK"
                settings_data = settings.get(name)

                if (settings_data['frob'] == '' and settings_data['token'] == ''):
                    flickr = Flickr()
                    back = flickr.generateToken()

                if (settings_data['frob'] != ''):
                    flickr = Flickr(frob = settings_data['frob'])
                    flickr.authenticate_save()
                    checkToken = flickr.checkToken();
                    
            else:
                form_info = "ERROR"
        return render_template("flickr_api.html",
                               form=settings_data,
                               form_info=form_info, back=back, checkToken=checkToken)

    except TemplateNotFound:
        abort(404)
