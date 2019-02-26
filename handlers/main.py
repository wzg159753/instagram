import tornado.web
from pycket.session import SessionMixin
from utils.photos import UploadImage
from utils.login_func import add_post_db, search_post_for, search_all_thum, get_post_id, get_like_post, get_like_count, get_user, del_upload_img, add_like, is_exits_like, del_like, add_atte, atte_is_exits, delete_atte


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
        # 显示是哪个用户上传的
        user = get_user(self.current_user)
        self.render('expract_page.html', data=data, user=user)

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
            post = add_post_db(ims.get_upload_path, ims.get_thumb_path, self.current_user)
            self.redirect('/post/{}'.format(post.id))


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
        m_user = get_user(self.current_user)
        # 判断当前是哪个用户， 可以查看别的用户的上传和喜欢的信息
        username = self.get_argument('name', '')
        if not username:
            username = self.current_user
        user = get_user(username)
        # 如果用户存在 就调用查找用户所有上传的方法， 将用户名传入
        posts = search_post_for(user.username)
        # 判断数据库用户是否关注
        atte = atte_is_exits(m_user.id, user.id)
        # 调用查找用户喜欢的图片方法
        like_post = get_like_post(user)
        self.render('profile_page.html',
                    user = user,
                    posts = posts,
                    like_post = like_post,
                    atte = atte
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
        if not is_exits_like(user.id, int(key)):
            add_like(user.id, int(key))
            self.redirect('/post/{}'.format(key))
            self.flush()
        else:
            # 如果有就删除
            del_like(user.id, int(key))



class DelHandler(BaseHandler):
    """
    删除自己上传的图片
    """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # 获取图片id 已经放到了单个图片页
        pid = int(kwargs['pid'])
        user = get_user(self.current_user)
        # 判断图片是否有人喜欢
        if is_exits_like(user.id, pid):
            # 如果有喜欢 就先把喜欢删除了
            del_like(user.id, pid)
        # 再删除这张图片
        del_upload_img(pid, user.id)
        self.redirect('/')


class AtteHandler(BaseHandler):
    """
    用户添加关注
    """
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        # 获取ajax传过来的uid  被关注人的id
        uid = self.get_argument('uid', '')
        # 获取关注人的id
        user = get_user(self.current_user)
        # 判断数据库是否已经关注 如果关注
        if atte_is_exits(user.id, int(uid)):
            # 就删除这个关注
            delete_atte(user.id, int(uid))
        else:
            # 如果没关注  就添加关注
            add_atte(user.id, int(uid))








