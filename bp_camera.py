from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from lib.settings import Settings
from flask import request
from flask.ext.login import login_required


bp_camera = Blueprint('bp_camera', __name__, template_folder='templates')


@bp_camera.route("/camera/<name>", methods=["GET", "POST"])
@login_required
def edit(name='youtube'):
    try:
        # name = youtube
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
        return render_template("camera_" + name + ".html",
                               form=settings_data,
                               form_info=form_info)

    except TemplateNotFound:
        abort(404)

