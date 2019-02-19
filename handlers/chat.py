import re
import uuid
from datetime import datetime
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import tornado.escape
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from .main import BaseHandler
from utils.photos import UploadImage
from utils.login_func import add_post_db


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

    @tornado.gen.coroutine
    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        body = parsed['body']
        url = re.search(r"(\bhttp.*\.jpg$)|(\bhttp.*\.png$)", body)
        if url:
            # # 方法一
            # client = AsyncHTTPClient()
            # resp = yield client.fetch('http://192.168.35.128:8080/async?url={}&user={}&from={}'.format(url.group(), self.current_user, 'async'))
            # post_id = resp.body.decode()
            # if post_id != 'Error':
            #     body = 'http://192.168.35.128:8080/post/{}'.format(post_id)
            # else:
            #     body = parsed['body']
            # 方法二
            client = AsyncHTTPClient()
            im = UploadImage('a.jpg', self.settings['static_path'])
            resp = yield client.fetch(url.group())
            im.save_upload(resp.body)
            im.save_thumb()
            post_id = add_post_db(im.get_upload_path, im.get_thumb_path, self.current_user)
            body = 'http://192.168.35.128:8080/post/{}'.format(str(post_id))


        chat = {
            'id': uuid.uuid4().hex,
            'user': self.current_user,
            'time': datetime.now(),
            'body': body
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