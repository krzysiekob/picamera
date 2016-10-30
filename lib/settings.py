# -*- coding: utf-8 -*-

import sqlite3 as lite
import os
import sys


class Settings:

    def __init__(self):
        self.db_path = os.getcwd() + '/lib/settings.lite'

    def get(self, section_name):
        sql = 'select option, value from settings where name=?';
        ret = {}
        for row in self._fetch(sql=sql, params=(section_name,)):
            ret[row[0]] = row[1]
        return ret

    def update(self, section_name, option, value):
        sql = 'update settings set value=? where name=? and option=?'
        return self._exc(sql=sql, params=(value, section_name, option))
    
    def set_form(self, form, section_name):
        for option, value in form.items():
            self.set_params(section_name, option, value)
        return True
    
    def set_params(self, section_name, option, value):
        self.update(section_name, option, value.encode('ascii', 'ignore'))
        return True

    def get_params(self, params):
        sql = 'select value from settings where name=? and option=?';
        ret = {}
        for row in self._fetch(sql=sql, params=(params[0], params[1])):
            ret[params[0]+'__'+params[1]] = row[0]
        return ret
        
    def insert(self, params):
        if (len(self.get_params(params)) == 0):
            print "insert"
            print params
            sql = 'insert into settings (name, option, value) values (?, ?, ?)'
            self._exc(sql, params)
        
    def setupDB(self):
        print "setupDB"
        sql = 'create table if not exists settings (name text, option text, value text)'
        self._exc(sql)
        self.default_insert()

    def _fetch(self, sql, params=None):
        con = None
        try:
            con = lite.connect(self.db_path)
            con.text_factory = str
            cur = con.cursor()
            rows = []
            if params is None:
                for row in cur.execute(sql):
                    rows.append(row)
            else:
                for row in cur.execute(sql, params):
                    rows.append(row)
            con.commit()
            con.close()
            return rows
        except lite.Error, e:
            print("Error: %s" % e.args[0])
            if con != None:
                con.close()
            sys.exit(1)
        finally:
            pass

    def _exc(self, sql, params=None):
        con = None
        try:
            con = lite.connect(self.db_path)
            con.text_factory = str
            cur = con.cursor()
            if params is None:
                cur.execute(sql)
            else:
                cur.execute(sql, params)
            con.commit()
            con.close()
        except lite.Error, e:
            print("Error: %s" % e.args[0])
            if con != None:
                con.close()
            sys.exit(1)
        finally:
            pass


    def default_insert(self):
        self.insert(('user', 'login', 'admin'))
        self.insert(('user', 'password', '$pbkdf2-sha256$1000$pBRCCGGsdc65lxLCWOs9xw$ZY0Z1I/lUqxMsz4N1Dd5cC/RlPZ8ClXftHb2eQhCYOw'))
        self.insert(('cron', 'is_power_cron', '1'))
        self.insert(('cron', 'email', ''))
        self.insert(('cron', 'subject1', ''))
        self.insert(('cron', 'subject2', ''))
        self.insert(('cron', 'subject3', ''))
        self.insert(('cron', 'subject4', ''))
        self.insert(('cron', 'subject5', ''))
        self.insert(('cron', 'subject6', ''))
        self.insert(('cron', 'subject7', ''))
        self.insert(('cron', 'subject8', ''))
        self.insert(('cron', 'subject9', ''))
        self.insert(('cron', 'subject10', ''))
        self.insert(('cron', 'subject11', ''))
        self.insert(('cron', 'subject12', ''))
        self.insert(('cron', 'subject13', ''))
        self.insert(('cron', 'subject14', ''))
        self.insert(('cron', 'subject15', ''))
        self.insert(('cron', 'time1', ''))
        self.insert(('cron', 'time2', ''))
        self.insert(('cron', 'time3', ''))
        self.insert(('cron', 'time4', ''))
        self.insert(('cron', 'time5', ''))
        self.insert(('cron', 'time6', ''))
        self.insert(('cron', 'time7', ''))
        self.insert(('cron', 'time8', ''))
        self.insert(('cron', 'time9', ''))
        self.insert(('cron', 'time10', ''))
        self.insert(('cron', 'time11', ''))
        self.insert(('cron', 'time12', ''))
        self.insert(('cron', 'time13', ''))
        self.insert(('cron', 'time14', ''))
        self.insert(('cron', 'time15', ''))
        self.insert(('email', 'is_power_gmail', '1'))
        self.insert(('email', 'gmail_user', 'foo@gmail.com'))
        self.insert(('email', 'gmail_pwd', 'password'))
        self.insert(('email', 'gmail_is_connect', '0'))
        self.insert(('email', 'gmail_imap', 'imap.gmail.com'))
        self.insert(('email', 'gmail_smtp', 'smtp.gmail.com'))
        self.insert(('email', 'gmail_smtp_port', '587'))
        self.insert(('email', 'gmail_smtp_max_size', '20000000'))
        self.insert(('email', 'email_smtp_accept_all', 'False'))
        self.insert(('email', 'email_smtp_accept', ''))
        self.insert(('email', 'email_subject', 'Pi'))
        self.insert(('email', 'email_subject_ping', 'Ping'))
        self.insert(('email', 'email_subject_streaming', 'Live'))
        self.insert(('email', 'email_txt_send', 'Witaj;;Pozdrawiam: Automat PI Camera;'))
        self.insert(('email', 'path_files', 'static/photo'))
        self.insert(('email', 'photo_default_length', '1'))
        self.insert(('email', 'photo_default_offset', '1'))
        self.insert(('email', 'is_power_photo', '1'))
        self.insert(('email', 'stop_photo', '22:00'))
        self.insert(('email', 'start_photo', '10:00'))
        self.insert(('email', 'step_photo', '10'))
        self.insert(('email', 'photo_sharpness', '0'))
        self.insert(('email', 'photo_contrast', '0'))
        self.insert(('email', 'photo_brightness', '50'))
        self.insert(('email', 'photo_saturation', '0'))
        self.insert(('email', 'photo_iso', '0'))
        self.insert(('email', 'photo_exposure_compensation', '0'))
        self.insert(('email', 'photo_exposure_mode', 'auto'))
        self.insert(('email', 'photo_meter_mode', 'average'))
        self.insert(('email', 'photo_awb_mode', 'auto'))
        self.insert(('email', 'photo_image_effect', 'none'))
        self.insert(('email', 'photo_color_effects', 'None'))
        self.insert(('email', 'photo_rotation', '180'))
        self.insert(('email', 'photo_hflip', 'False'))
        self.insert(('email', 'photo_vflip', 'False'))
        self.insert(('email', 'photo_crop', '0.0, 0.0, 1.0, 1.0'))
        self.insert(('email', 'photo_awb_gains_blue', '4'))
        self.insert(('email', 'photo_awb_gains_red', '1.9'))
        self.insert(('email', 'photo_color_effects_u', ''))
        self.insert(('email', 'photo_color_effects_v', ''))
        self.insert(('email', 'photo_zoom_x', '0'))
        self.insert(('email', 'photo_zoom_y', '0'))
        self.insert(('email', 'photo_zoom_w', '1'))
        self.insert(('email', 'photo_zoom_h', '1'))
        self.insert(('email', 'photo_annotate_background', '#000000'))
        self.insert(('email', 'photo_annotate_text', ''))
        self.insert(('email', 'photo_annotate_size', '40'))
        self.insert(('email', 'photo_annotate_add_date', '1'))
        self.insert(('email', 'photo_resolution', '2592x1944'))
        self.insert(('youtube', 'youtube_stream_url', 'rtmp://a.rtmp.youtube.com/live2'))
        self.insert(('youtube', 'youtube_stream_id', 'your stream id'))
        self.insert(('youtube', 'url_live', 'http://www.youtube.com/c/USER/live'))

        self.insert(('bash', 'yt_start', 'raspivid -o - -t 0 -w 1280 -h 720 -fps 25 -b 4000000 -g 50 | /home/pi/youtube/arm/bin/ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv [youtube_stream_id]'))
        self.insert(('bash', 'yt_stop', 'killall ffmpeg; killall raspivid'))
        self.insert(('flickr', 'api_key', ''))
        self.insert(('flickr', 'secret', ''))
        self.insert(('flickr', 'token', ''))
        self.insert(('flickr', 'frob', ''))
        self.insert(('flickr', 'title', ''))
        self.insert(('flickr', 'description', ''))
        self.insert(('flickr', 'tags', 'auto-upload'))
        self.insert(('flickr', 'is_private', '1'))
        self.insert(('flickr', 'is_public', '0'))
        self.insert(('flickr', 'is_family', '0'))
        self.insert(('flickr', 'is_friend', '0'))
        self.insert(('flickr', 'is_power', '0'))
        self.insert(('flickr', 'album_format', '%Y'))

