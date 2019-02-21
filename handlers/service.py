import tornado.gen
import tornado.web
from tornado.httpclient import AsyncHTTPClient
import tornado.escape
from .main import BaseHandler
from utils.photos import UploadImage
from utils.login_func import add_post_db
from .chat import MessageHandler, make_chat


class AsyncHandler(BaseHandler):
    """
    内部API接口
    """
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        url = self.get_argument('url', '')
        user = self.get_argument('user', '')
        is_extis_from = self.get_argument('from', '')
        if user and is_extis_from == 'async':
            client = AsyncHTTPClient()
            resp = yield client.fetch(url)
            im = UploadImage('a.jpg', self.settings['static_path'])
            im.save_upload(resp.body)
            im.save_thumb()
            post = add_post_db(im.get_upload_path, im.get_thumb_path, user)
            body = 'http://192.168.35.128:8080/post/{}'.format(post.id)
            # 不加image参数是只显示url， 加上就直接显示出图片
            chat = make_chat(body, user, post.thumb_url, post.id) # 调用格式化参数方法
            msg1 = {
                # 这里用了tornado自带的将模板转移为字符串并发送给浏览器解析
                'html': tornado.escape.to_basestring(
                    # 将chat传到模板
                    self.render_string('message.html', message=chat)
                )
            }
            MessageHandler.add_history(msg1) # 在接口发送新消息就要调用MessageHandler的类方法
            MessageHandler.send_message(msg1)
        else:
            self.write('Error')