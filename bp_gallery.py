from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from lib.settings import Settings
import os
import glob
from flask.ext.paginate import Pagination
from flask.ext.login import login_required
from flask import redirect
from flask import url_for

bp_gallery = Blueprint('bp_gallery', __name__, template_folder='templates')


@bp_gallery.route("/gallery", methods=["GET"])
@bp_gallery.route("/gallery/<int:page>", methods=["GET"])
@login_required
def edit(page=1):
    try:
        settings = Settings()
        settings_data = settings.get("email")
        files = glob.glob(settings_data["path_files"] + "/*.jpg")
        files.sort(key=os.path.getctime, reverse=True)
        offset = 8
        end = page * offset
        start = end - offset
        pagination = Pagination(page=page, total=len(files))
        return render_template("gallery.html",
                               files=files[start:end],
                               pagination=pagination)

    except TemplateNotFound:
        abort(404)


@bp_gallery.route("/gallery_clear", methods=["GET"])
@login_required
def clear():
    try:
        settings = Settings()
        settings_data = settings.get("email")

        my_files = []
        for root, dirs, files in os.walk(settings_data["path_files"]):
            for filename in files:
                my_files.append(os.path.join(root, filename))

        for my_file in my_files:
            if '.jpg' == os.path.splitext(my_file)[1]:
                os.remove(my_file)

        return redirect(url_for('bp_gallery.edit'))

    except TemplateNotFound:
        abort(404)
