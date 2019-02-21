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
from tornado.ioloop import IOLoop



def make_chat(body, name='admin', image=None, post_id=None):
    """
    生成一个格式化的参数字典Dict
    :param body:
    :param name:
    :return:
    """
    return {
        'id': uuid.uuid4().hex,
        'user': name,
        'time': datetime.now(),
        'body': body,  # 将信息保存到value
        'image': image,
        'post_id': post_id
    }

class SessionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('room.html', messages=MessageHandler.history)


class MessageHandler(WebSocketHandler, BaseHandler):
    user = set() # 集合  用于用户去重
    history = [] # 保存历史信息
    size = 100 # 保存的最大历史信息消息

    def open(self, *args, **kwargs):
        """
        用户连接
        :param args:
        :param kwargs:
        :return:
        """
        print('用户-{}—{}-{}-连接'.format(self.current_user, self.request.remote_ip, datetime.now()))
        MessageHandler.user.add(self)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message) # 将ajax传来json解码
        body = parsed['body'] # 取出内容 ajax里面自定义的
        url = re.search(r"(\bhttp.*\.jpg$)|(\bhttp.*\.png$)", body) # 判断是不是一个图片
        if url:
            # # 方法一
            url = 'http://192.168.35.128:8080/async?url={}&user={}&from={}'.format(url.group(), self.current_user, 'async')
            client = AsyncHTTPClient()
            IOLoop.current().spawn_callback(client.fetch, url)
            # resp = yield client.fetch(url)
            # post_id = resp.body.decode()
            # if post_id != 'Error':
            #     body = 'http://192.168.35.128:8080/post/{}'.format(post_id)
            body = 'url {} is processing'.format(url)
            chat = make_chat(body)
            msg1 = {
                # 这里用了tornado自带的将模板转移为字符串并发送给浏览器解析
                'html': tornado.escape.to_basestring(
                    # 将chat传到模板
                    self.render_string('message.html', message=chat)
                )
            }
            self.write_message(msg1)

        else:
            chat = make_chat(body, self.current_user)
            msg1 = {
                # 这里用了tornado自带的将模板转移为字符串并发送给浏览器解析
                'html': tornado.escape.to_basestring(
                    # 将chat传到模板
                    self.render_string('message.html', message = chat)
                )
            }
            MessageHandler.add_history(msg1)
            MessageHandler.send_message(msg1)

    def on_close(self):
        """
        用户退出
        :return:
        """
        print('用户-{}-{}-{}-退出'.format(self.current_user, self.request.remote_ip, datetime.now()))
        MessageHandler.user.remove(self)

    @classmethod
    def add_history(cls, msg):
        """
        保存历史信息
        :param msg:
        :return:
        """
        cls.history.append(msg)
        if len(cls.history) > cls.size:
            # 如果历史信息大于200条 则取-200条
            cls.history = cls.history[-cls.size:]

    @classmethod
    def send_message(cls, msg):
        """
        发送消息
        :param msg:
        :return:
        """
        for w in MessageHandler.user:
            w.write_message(msg)











# 方法二
# client = AsyncHTTPClient() # 实例化异步客户端
# im = UploadImage('a.jpg', self.settings['static_path']) # 实例化上传图片类
# resp = yield client.fetch(url.group()) # 对这个图片发起请求 下载
# im.save_upload(resp.body) # 保存uploads
# im.save_thumb() # 保存缩略图
# post_id = add_post_db(im.get_upload_path, im.get_thumb_path, self.current_user) # 将图片添加到用户上传
# # 将这条url赋值给body 用作发送到聊天室
# body = 'http://192.168.35.128:8080/post/{}'.format(str(post_id))

# # 方法二
# msg = {
#     'html': tornado.escape.to_basestring('<div class="message" id="m{}">{}</div>'.format(chat['id'], chat['body']))
# }