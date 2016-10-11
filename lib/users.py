# -*- coding: utf-8 -*-

import flask.ext.login as flask_login
from lib.settings import Settings
from passlib.hash import pbkdf2_sha256


class User(flask_login.UserMixin):

    def login(self, login, password):
        settings = Settings()
        settings_user = settings.get('user')
        if login == settings_user['login'] and pbkdf2_sha256.verify(password, settings_user['password']):
            self.id = login
            return True
        return False

    def get_by_login(self, login):
        settings = Settings()
        settings_user = settings.get('user')
        if login == settings_user['login']:
            self.id = login
            return True
        return False

    def password(self, pw1, pw2):
        pw1 = pbkdf2_sha256.encrypt(pw1, rounds=1000, salt_size=16)
        if pbkdf2_sha256.verify(pw2, pw1) is False:
            return False
        settings = Settings()
        form = {'password': pw1}
        if settings.set_form(form=form,
                             section_name='user') is True:
            return True

        return False
