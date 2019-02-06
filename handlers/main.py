import tornado.web
from utils.photos import save_upload, save_suo


class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index_page.html')

class expraceHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('expract_page.html')

class PostHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('post_page.html',
                    number = kwargs['number']
                    )

class UploadHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('upload_page.html')

    def post(self, *args, **kwargs):
        # 获取提交的图片信息filename 图片名***.jpg  body图片二进制数据,
        file_list = self.request.files.get('filename')
        for file in file_list:
            name = file['filename']
            content = file['body']
            save_upload(name, content) # 保存到上传文件夹
            save_suo(name, (200, 200)) # 保存缩略图， 用于expract_page页面展示


