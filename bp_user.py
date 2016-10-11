# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
import flask
from lib.users import User
import flask.ext.login as flask_login
from flask.ext.login import login_required


bp_user = Blueprint('bp_user', __name__, template_folder='templates')


@bp_user.route('/login', methods=['GET', 'POST'])
def login():

    if flask.request.method == 'POST':

        for k, v in flask.request.form.items():
            if k == 'login':
                login = v
            if k == 'password':
                password = v

        user = User()
        if user.login(login, password):
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('bp_home.edit'))

    return render_template("login.html")


@bp_user.route('/password', methods=['GET', 'POST'])
@login_required
def password():

    if flask.request.method == 'POST':

        for k, v in flask.request.form.items():
            if k == 'pw1':
                pw1 = v
            if k == 'pw2':
                pw2 = v

        user = User()
        if user.password(pw1, pw2):
            return flask.redirect(flask.url_for('bp_user.logout'))

    return render_template("password.html")


@bp_user.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('bp_user.login'))
