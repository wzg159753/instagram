import tornado.gen
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from .main import BaseHandler
from utils.photos import UploadImage
from utils.login_func import add_post_db

class AsyncHandler(BaseHandler):

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
            post_id = add_post_db(im.get_upload_path, im.get_thumb_path, user)
            self.write(str(post_id))
        else:
            self.write('Error')