import tornado.web
from handlers.main import BaseHandler
from utils.login_func import verify_login, note_user


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        next = self.get_argument('next', '')
        self.render('login_page.html',
                    next = next
                    )

    def post(self, *args, **kwargs):
        next = self.get_argument('next', '')
        username = self.get_argument('username', None)
        password = self.get_argument('pwd', None)
        info = verify_login(username, password)
        if next:
            if info:
                self.set_session(username, next)
            else:
                self.write('用户名或密码错误')
        else:
            self.set_session(username, '/')

    def set_session(self, username, login):
        self.session.set('user_id', username)
        self.redirect(login)


class SigupHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render('signup_page.html')

    def post(self, *args, **kwargs):
        username = self.get_argument('username', '')
        number = self.get_argument('number', '')
        password = self.get_argument('password', '')
        password1 = self.get_argument('password1', '')
        content = note_user(username, number, password, password1)
        if not content:
            self.session.set('user_id', username)
            self.redirect('/')
        else:
            self.write(content)

