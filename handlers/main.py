import tornado.web


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