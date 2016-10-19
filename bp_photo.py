from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from flask import request
from flask.ext.login import login_required
from lib.settings import Settings


bp_photo = Blueprint('bp_photo', __name__, template_folder='templates')

@bp_photo.route("/photo/<string:type>", methods=["GET", "POST"])
@login_required
def edit(type):
    try:
        name = 'email'
        settings = Settings()
        settings_data = settings.get(name)
                
        form_info = ""
        if request.method == 'POST':
            if settings.set_form(form=request.form,
                                 section_name=name) is True:
                form_info = "OK"
                settings_data = settings.get(name)
            else:
                form_info = "ERROR"

        return render_template("photo_" + type + ".html", form = settings_data, form_info=form_info)

    except TemplateNotFound:
        abort(404)
