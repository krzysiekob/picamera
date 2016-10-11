# -*- coding: utf-8 -*-
# http://flask.pocoo.org/snippets/116/

from flask import Blueprint
import gevent
from gevent.queue import Queue
from flask import request
from lib.settings import Settings
from flask import Response
from gevent import subprocess
import logging
from flask.ext.login import login_required


bp_server_send_event = Blueprint('bp_server_send_event',
                                 __name__,
                                 template_folder='templates')


class ServerSentEvent(object):

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)

subscriptions = []


def notify():
    command = ["raspivid"]
    i = 1
    while True:
        for p in command:
            try:
                subprocess.check_output(["pidof", p])
                for sub in subscriptions[:]:
                    sub.put("[%s] Transmisja włączona" % i)
                    gevent.sleep(1)
                    i += 1
            except:
                pass

gevent.spawn(notify)


@bp_server_send_event.route("/debug")
@login_required
def debug():
    return "Currently %d subscriptions" % len(subscriptions)


@bp_server_send_event.route("/publish", methods=["POST"])
@login_required
def publish():
    settings = Settings()
    settings_bash = settings.get('bash')

    action = ''
    command_start = ''
    command_stop = ''
    for ky, val in request.form.items():
        if ky == 'id':
            action = val
        if ky == 'sh':
            command_start = settings_bash[val + "_start"]
            command_stop = settings_bash[val + "_stop"]
        if ky == 'yt_id':
            command_start = command_start.replace(
                '[youtube_stream_id]', val)

    if action == 'start':
        if command_start == '':
            return "FAIL"
        try:
            subprocess.check_output(["pidof", 'raspivid'])
        except:
            logging.getLogger("app").debug(command_start)
            subprocess.Popen(command_start, shell=True, stdout=subprocess.PIPE)

    if action == 'stop':
        if command_stop == '':
            return "FAIL"
        subprocess.Popen(command_stop, shell=True, stdout=subprocess.PIPE)

    return "OK"


@bp_server_send_event.route("/subscribe")
@login_required
def subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit:  # Or maybe use flask signals
            subscriptions.remove(q)

    return Response(gen(), mimetype="text/event-stream")
