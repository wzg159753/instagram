import glob
import tornado.web
from pycket.session import SessionMixin
from utils.photos import UploadImage
from sql_dbs.modules import Like, Post
from utils.login_func import add_post_db, search_post_for, search_all_thum, get_post_id, get_like_post, get_like_count, get_user


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        return self.session.get('user_id', None)

class MainHandler(BaseHandler):
    """
    根路由， 用于展示当前用户上传的所有大图
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 将当前用户传入， 查找user.post一个关联查询 返回post实例
        data = search_post_for(self.current_user)
        self.render('index_page.html', data=data)


class expraceHandler(BaseHandler):
    """
    展示所有缩略图逻辑
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 一个简单的调用， 按照上传时间展示缩略图
        data = search_all_thum()
        self.render('expract_page.html', data=data)

class PostHandler(BaseHandler):
    """
    单张图片展示， 用于点击图片， 跳到大图页
    """
    def get(self, *args, **kwargs):
        # 拿到传入的post_id和Post.id做查询
        post = get_post_id(kwargs['number'])
        if post:
            # 如果存在， 调用统计喜欢人数的方法， 将post实例传入
            like_count = get_like_count(post)
            self.render('post_page.html',
                        post=post,
                        like_count = like_count
                        )

class UploadHandler(BaseHandler):
    """
    用户上传图片逻辑， 并保存图片， 保存缩略图， 将图片路径添加到数据库
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('upload_page.html')

    def post(self, *args, **kwargs):
        # 获取提交的图片信息filename 图片名***.jpg  body图片二进制数据,
        file_list = self.request.files.get('filename')
        for file in file_list:
            name = file['filename'] # 图片名***.jpg
            content = file['body'] # 图片二进制数据
            ims = UploadImage(name, self.settings['static_path']) # 实例化上传图片类
            ims.save_upload(content) # 保存到上传文件夹
            ims.save_thumb() # 保存缩略图， 用于expract_page页面展示
            post_id = add_post_db(ims.get_upload_path, ims.get_thumb_path, self.current_user)
            self.redirect('/post/{}'.format(post_id))


class LogunoutHandler(BaseHandler):
    """
    用户退出逻辑
    """
    def get(self, *args, **kwargs):
        self.session.delete('user_id')
        self.redirect('/login')


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 判断当前是哪个用户， 可以查看别的用户的上传和喜欢的信息
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
                    posts = posts,
                    like_post = like_post
                    )


class TestHandler(BaseHandler):
    """
    用户点击喜欢，再点击一次就取消喜欢
    """
    def post(self, *args, **kwargs):
        # 获取post_id 在模板里表现为一个span标签  后端js用.innerText 提取文本
        key = self.get_body_argument('post_id', '')
        # 调用get_user获取当前用户的user_id
        user = get_user(self.current_user)
        # 要先判断数据库中有没有这个喜欢， 没有就添加
        if not Like.is_exits_like(user.id, int(key)):
            Like.add_like(user.id, int(key))
        else:
            # 如果有就删除
            Like.del_like(user.id, int(key))


class DelHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        pid = int(kwargs['pid'])
        user = get_user(self.current_user)
        if Like.is_exits_like(user.id, pid):
            Like.del_like(user.id, pid)
        Post.del_upload_img(pid, user.id)
        self.write('over')





