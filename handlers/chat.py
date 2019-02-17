import uuid
from datetime import datetime
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import tornado.escape
from .main import BaseHandler


class SessionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('room.html', messages=MessageHandler.history)


class MessageHandler(WebSocketHandler, BaseHandler):
    user = set()
    history = []
    size = 100

    def open(self, *args, **kwargs):
        print('用户-{}—{}-{}-连接'.format(self.current_user, self.request.remote_ip, datetime.now()))
        MessageHandler.user.add(self)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        chat = {
            'id': uuid.uuid4().hex,
            'user': self.current_user,
            'time': datetime.now(),
            'body': parsed['body']
        }
        msg1 = {
            'html': tornado.escape.to_basestring(
                self.render_string('message.html', message = chat)
            )
        }
        msg = {
            'html': tornado.escape.to_basestring('<div class="message" id="m{}">{}</div>'.format(chat['id'], chat['body']))
        }
        MessageHandler.add_history(msg1)
        MessageHandler.send_message(msg1)

    @classmethod
    def add_history(cls, msg):
        cls.history.append(msg)
        if len(cls.history) > cls.size:
            cls.history = cls.history[-cls.size:]

    @classmethod
    def send_message(cls, msg):
        for w in MessageHandler.user:
            w.write_message(msg)

    def on_close(self):
        print('用户-{}-{}-{}-退出'.format(self.current_user, self.request.remote_ip, datetime.now()))
        MessageHandler.user.remove(self)