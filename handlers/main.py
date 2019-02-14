import glob
import tornado.web
from pycket.session import SessionMixin
from utils.photos import UploadImage
from utils.login_func import add_post_db, search_post_for, search_all_thum, get_post_id


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        return self.session.get('user_id', None)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # data = glob.glob('static/uploads/*')
        data = search_post_for(self.current_user)
        self.render('index_page.html', data=data, username=self.current_user)


class expraceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        data = search_all_thum()
        self.render('expract_page.html', data=data, username=self.current_user)

class PostHandler(BaseHandler):
    def get(self, *args, **kwargs):
        number = get_post_id(kwargs['number'])
        self.render('post_page.html',
                    number=number,
                    username=self.current_user
                    )

class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('upload_page.html', username=self.current_user)

    def post(self, *args, **kwargs):
        # 获取提交的图片信息filename 图片名***.jpg  body图片二进制数据,
        file_list = self.request.files.get('filename')
        for file in file_list:
            name = file['filename']
            content = file['body']
            ims = UploadImage(name, 'static')
            ims.save_upload(content) # 保存到上传文件夹
            ims.save_thumb() # 保存缩略图， 用于expract_page页面展示
            post_id = add_post_db(ims.get_upload_path, ims.get_thumb_path, self.current_user)
            self.redirect('/post/{}'.format(post_id))


class LogunoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.session.delete('user_id')
        self.redirect('/login')


