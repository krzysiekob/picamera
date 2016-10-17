from flask import Blueprint
from flask import render_template
from flask import abort
from jinja2 import TemplateNotFound
from lib.photo import Photo
from flask import request
import os
import time
from flask.ext.login import login_required
from collections import namedtuple
from lib.settings import Settings

_ntuple_diskusage = namedtuple('usage', 'total used free')


def disk_usage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)


bp_home = Blueprint('bp_home', __name__, template_folder='templates')
    
@bp_home.route("/home", methods=["GET", "POST"])
@login_required
def edit():
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
                

        image = 'static/test.jpg'
        if request.method == 'POST':
            p = Photo(path=None)
            p.create_image(image)

        date_created = ''
        try:
            date_created = time.ctime(os.path.getctime(image))
        except:
            image = ''
            pass
        
        return render_template("home.html",
                               image=image,
                               date_created=date_created, form = settings_data)

    except TemplateNotFound:
        abort(404)

@bp_home.route("/", methods=["GET"])
@login_required
def index():
    try:        
        return render_template("index.html", disk=disk_usage("/") )

    except TemplateNotFound:
        abort(404)
