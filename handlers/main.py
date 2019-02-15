import glob
import tornado.web
from pycket.session import SessionMixin
from utils.photos import UploadImage
from sql_dbs.modules import Like
from utils.login_func import add_post_db, search_post_for, search_all_thum, get_post_id, get_like_post, get_like_count, get_user


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        return self.session.get('user_id', None)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        data = search_post_for(self.current_user)
        self.render('index_page.html', data=data, username=self.current_user)


class expraceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        data = search_all_thum()
        self.render('expract_page.html', data=data, username=self.current_user)

class PostHandler(BaseHandler):
    def get(self, *args, **kwargs):
        post = get_post_id(kwargs['number'])
        if post:
            like_count = get_like_count(post)
            self.render('post_page.html',
                        post=post,
                        username=self.current_user,
                        like_count = like_count
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


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 调用User模板的判断用户存在方法
        username = self.get_argument('name', '')
        if not username:
            username = self.current_user
        user = get_user(username)
        # 如果用户存在 就调用查找用户所有上传的方法， 将用户名传入
        posts = search_post_for(user.username)
        # 调用查找用户喜欢的图片方法
        like_post = get_like_post(user)
        self.render('profile_page.html',
                    user = user,
                    username=self.current_user,
                    posts = posts,
                    like_post = like_post
                    )


class TestHandler(BaseHandler):
    def post(self, *args, **kwargs):
        key = self.get_body_argument('post_id', '')
        user = get_user(self.current_user)
        if not Like.is_exits_like(user.id, int(key)):
            Like.add_like(user.id, int(key))
        else:
            Like.del_like(user.id, int(key))




