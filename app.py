import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from handlers import main, chat, service
from handlers import verify


define('port', default=8080, help='run_port', type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handler = [
            (r'/', main.MainHandler),
            (r'/expract', main.expraceHandler),
            (r'/upload', main.UploadHandler),
            (r'/login', verify.LoginHandler),
            (r'/signup', verify.SigupHandler),
            (r'/loginout', main.LogunoutHandler),
            (r'/profile', main.ProfileHandler),
            (r'/test', main.TestHandler),
            (r'/session', chat.SessionHandler),
            (r'/ws', chat.MessageHandler),
            (r'/post/(?P<number>[0-9]+)', main.PostHandler),
            (r'/async', service.AsyncHandler),
            (r'/del/(?P<pid>[0-9]+)', main.DelHandler)
        ]

        settings = dict(
            debug = True,
            template_path = 'template',
            static_path = 'static',
            login_url = '/login',
            cookie_secret = 'hello_world',
            pycket = {
                'engine': 'redis',
                'storage': {
                    'host': 'localhost',
                    'port': 6379,
                    'db_sessions': 5,
                    'max_connections': 2**30
                },
                'cookies': {
                    'expires_days': 30
                }
            }
        )

        super().__init__(handler, **settings)


if __name__ == '__main__':
    app = Application()
    tornado.options.parse_command_line()
    app.listen(options.port)
    print('run server as port {}'.format(options.port))
    tornado.ioloop.IOLoop.current().start()