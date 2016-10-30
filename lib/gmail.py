# -*- coding: utf-8 -*-

import sys
import imaplib
import email
import email.header
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import os
import glob
import time
from lib.settings import Settings
import re
import logging
import ast
import gevent
from gevent import subprocess
from datetime import datetime


class Gmail():

    def __init__(self):
        settings = Settings()
        s = settings.get("email")
        self.is_power_gmail = int(s["is_power_gmail"])
        self.gmail_user = s["gmail_user"]
        self.gmail_pwd = s["gmail_pwd"]
        self.gmail_is_connect = s["gmail_is_connect"]
        self.gmail_imap = s["gmail_imap"]
        self.gmail_smtp = s["gmail_smtp"]
        self.gmail_smtp_port = int(s["gmail_smtp_port"])
        self.gmail_smtp_max_size = int(s["gmail_smtp_max_size"])

        self.email_smtp_accept_all = ast.literal_eval(
            s["email_smtp_accept_all"])
        self.email_smtp_accept = s["email_smtp_accept"].split(",")
        self.email_subject = s["email_subject"]
        self.email_subject_ping = s["email_subject_ping"]
        self.email_subject_streaming = s['email_subject_streaming']
        self.email_txt_send = s["email_txt_send"]
        self.path_files = s["path_files"]
        self.photo_default_length = int(s["photo_default_length"])
        self.photo_default_offset = int(s["photo_default_offset"])

        self.settings_bash = settings.get('bash')
        self.settings_youtube = settings.get('youtube')
        self.settings_cron = settings.get('cron')

        self.log = logging.getLogger("app")

    def pong(self, to, subject='pong', content='email testowy'):
        smtpserver = smtplib.SMTP(self.gmail_smtp, self.gmail_smtp_port)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(self.gmail_user, self.gmail_pwd)
        header = 'To:' + to + '\n' + 'From: ' + \
            self.gmail_user + '\n' + 'Subject: ' + subject + ' \n'
        msg = header + '\n ' + content + ' \n\n'
        smtpserver.sendmail(self.gmail_user, to, msg)
        self.log.debug(str(subject) + ' done!')
        smtpserver.close()

    def streaming(self, to, action, type_stream):
        content = ''
        try:
            command_start = self.settings_bash[type_stream + "_start"]
            command_stop = self.settings_bash[type_stream + "_stop"]
            if type_stream == 'yt':
                r = "%s/%s" % (self.settings_youtube["youtube_stream_url"],
                               self.settings_youtube["youtube_stream_id"])
                command_start = command_start.replace('[youtube_stream_id]', r)
                content = self.settings_youtube["url_live"]

            if action == 'start':
                try:
                    subprocess.check_output(["pidof", 'raspivid'])
                except:
                    logging.getLogger("app").debug(command_start)
                    subprocess.Popen(command_start, shell=True,
                                     stdout=subprocess.PIPE)

            if action == 'stop':
                subprocess.Popen(command_stop, shell=True,
                                 stdout=subprocess.PIPE)
        except Exception as e:
            self.pong(to,
                      subject="Exception Error:" + action + "," + type_stream,
                      content=str(e))

        title = "%s,%s,(%s)" % (action,
                                type_stream,
                                formatdate(localtime=True))
        try:
            subprocess.check_output(["pidof", 'raspivid'])
            self.pong(to, subject="Wlaczony:" + title, content=content)
        except:
            self.pong(to, subject="Wylaczony:" + title, content=content)

    def send_photo(self, to, files, return_subject):
        self.log.debug("send files:")
        self.log.debug(str(files))

        smtpserver = smtplib.SMTP(self.gmail_smtp, self.gmail_smtp_port)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(self.gmail_user, self.gmail_pwd)

        COMMASPACE = ', '
        msg = MIMEMultipart()
        msg["From"] = self.gmail_user
        msg["To"] = COMMASPACE.join(to)
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = return_subject

        msg.attach(MIMEText(self.email_txt_send.replace(";", "\n")))

        for f in files or []:
            with open(f, "rb") as fil:
                ct_name = time.ctime(os.path.getctime(f)) + "__" + basename(f)
                msg.attach(MIMEApplication(
                    fil.read(),
                    Content_Disposition='attachment; filename="%s"' % ct_name,
                    Name=ct_name
                ))

        smtpserver.sendmail(self.gmail_user, to, msg.as_string())
        self.log.debug('DONE!')
        smtpserver.close()

    def process_mailbox(self, M):
        M.select('inbox')
        rv, data = M.search(None, '(UNSEEN)')
        if rv != 'OK':
            self.log.debug("No messages found!")
            return

        for num in data[0].split():
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                self.log.error("Getting message %s" % num)
                return

            msg = email.message_from_string(data[0][1])
            from_email = email.header.decode_header(msg['From'])
            to = self.search_email(from_email)
            self.log.debug("to: %s" % str(to))

            if self.email_access(to=to) is False:
                self.log.debug("Access denied: %s" % str(to))
                continue

            decode = email.header.decode_header(msg['Subject'])[0]
            subject = decode[0].decode('utf-8')
            self.log.debug('Message %s: %s' % (num, subject))

            if self.email_subject_ping == subject:
                self.pong(to=to)
                continue

            self.process_streaming(to=[to], subject=subject)
            self.process_send_photo(to=[to], subject=subject)

    def process_streaming(self, to, subject):
        match = "^%s,(yt),(start|stop)$" % self.email_subject_streaming
        params_streaming = re.findall(match, subject)
        if len(params_streaming) == 1:
            self.streaming(to=to,
                           action=params_streaming[0][1],
                           type_stream=params_streaming[0][0])

    def process_send_photo(self, to, subject):
        if subject.find(self.email_subject) == -1:
            return

        split_photo_send = self.split_photo_send(subject)
        part_photo = len(split_photo_send)
        for k, files in split_photo_send.items():
            return_subject = u"Odp: %s" % subject
            if part_photo > 1:
                return_subject += u", part %s/%s" % (k + 1, part_photo)
            return_subject += " (%s)" % formatdate(localtime=True)

            self.log.debug("process_mailbox")
            self.log.debug(return_subject)
            self.log.debug(str(files))

            self.send_photo(to=to, files=files,
                            return_subject=return_subject)

    def email_access(self, to):
        if self.email_smtp_accept_all:
            self.log.debug("All email smtp accept")
            return True
        else:
            for email_access in self.email_smtp_accept:
                if len(re.findall("<(" + email_access + ")>", to)) > 0:
                    return True
        return False

    def search_email(self, efrom):
        for e in efrom:
            if e[0].find('@') == -1:
                self.log.debug("Invalid email: %s" % str(e[0]))
            else:
                return e[0]
        return None

    def split_photo_send(self, subject):
        params = re.findall(self.email_subject +
                            ",([0-9]+?),([0-9]+?)$", subject)
        if len(params) == 0:
            params = [(self.photo_default_length,
                       self.photo_default_offset)]

        length = int(params[0][0])
        offset = int(params[0][1])

        self.log.debug("Length: %s" % length)
        self.log.debug("Offset: %s" % offset)

        files = glob.glob(self.path_files + "/*.jpg")
        files.sort(key=os.path.getctime, reverse=True)
        files_send = []
        i = 1
        for file in files:
            if i == 1:
                files_send.append(file)
            i += 1
            if i > offset:
                i = 1

        return self._split(files=files_send[:length])

    def _split(self, files):
        s_files = {}
        size_sum = 0
        i = 0
        for file in files:
            size_sum += os.path.getsize(file)
            if i not in s_files:
                s_files[i] = []
            s_files[i].append(file)
            if size_sum >= self.gmail_smtp_max_size:
                i += 1
                size_sum = 0
        return s_files

    def check_connect(self, user=None, pwd=None):
        if user is None and pwd is None:
            user = self.gmail_user
            pwd = self.gmail_pwd
        
        M = imaplib.IMAP4_SSL(self.gmail_imap)
        try:
            rv, data = M.login(user, pwd)
            return True
        except imaplib.IMAP4.error:
            return False
    
    def run(self,):
        while True:
            if (self.is_power_gmail == 0):
                self.log.debug("Email is not power")
                self.__init__()
                gevent.sleep(5)                
                continue
            if (self.gmail_is_connect == '0'):
                self.log.debug("Brak skonfigurowanego email")
                self.__init__()
                gevent.sleep(5)
                continue
            try:
                M = imaplib.IMAP4_SSL(self.gmail_imap)
                try:
                    rv, data = M.login(self.gmail_user, self.gmail_pwd)
                except imaplib.IMAP4.error:
                    self.log.error("1 Login failed!!! ")
                    gevent.sleep(300)
                    self.__init__()
                    continue
                self.log.debug("login status: %s" % rv)
                self.log.debug("login email: %s" % data)

                i = 0
                while True:
                    self.process_mailbox(M)
                    gevent.sleep(1)
                    i += 1
                    if i > 120:
                        break

                M.close()
                M.logout()
                self.__init__()
                gevent.sleep(1)
            except imaplib.IMAP4.error:
                self.log.error("2 Login failed!!! ")
            except Exception as e:
                self.log.error("Gmail Error 1" + str(e))

    def cron(self,):
        while True:
            if (self.settings_cron["is_power_cron"] == "0"):
                self.log.debug("Cron is not power")
                self.__init__()
                gevent.sleep(5)
                continue
            try:
                to = self.settings_cron['email'].split(',')
                for i in range(1, 16):
                    if datetime.now().strftime('%H:%M') == self.settings_cron['time' + str(i)]:
                        subject = self.settings_cron['subject' + str(i)]
                        self.log.debug("cron %s %s" % (str(to), str(subject)))
                        self.process_streaming(to=to, subject=subject)
                        self.process_send_photo(to=to, subject=subject)

                self.__init__()
                gevent.sleep(60)
            except Exception as e:
                self.log.error("Gmail Error 2" + str(e))
