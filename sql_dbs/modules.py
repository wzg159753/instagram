from datetime import datetime
from sql_dbs.connect import Base, session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, exists
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=True)
    password = Column(String(50), nullable=True)
    number = Column(String(11), default='0000')
    create_time = Column(DateTime, default=datetime.now)
    users = relationship('Post', backref='posts', cascade='all')

    def __repr__(self):
        return '''
            <User>++id={}, username={}, password={}, number={}, create_time={}
        '''.format(
            self.id,
            self.username,
            self.password,
            self.username,
            self.create_time
        )

    @classmethod
    def add_user(cls, username, password, number):
        """
        添加用户
        :param username:
        :param password:
        :param number:
        :return:
        """
        session.add(User(username=username, password=password, number=number))
        session.commit()

    @classmethod
    def search(cls, username, password):
        """
        查找用户  用于登录验证
        :param username:
        :param password:
        :return:
        """
        return session.query(User).filter(User.username == username, User.password == password).first()

    @classmethod
    def is_exists(cls, username):
        """
        判断用户存不存在  用于注册
        :param username:
        :return:
        """
        return session.query(User).filter(exists().where(User.username == username)).first()

    @classmethod
    def search_posts(cls, username):
        """
        查找用户上传的图片 展示在首页
        :param username:
        :return:
        """
        return session.query(User).filter_by(username=username).first()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    img_url = Column(String(100), nullable=True)
    thumb_url = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    user_post = relationship('User', backref='post', uselist=False, cascade='all')

    def __repr__(self):
        return '''
            <Article>++id={}, img_url={}, thumb_url={}, user_id={}
            '''.format(
            self.id,
            self.img_url,
            self.thumb_url,
            self.user_id
        )

    @classmethod
    def del_upload_img(cls, pid, user_id):
        data = session.query(cls).filter(cls.id == pid, cls.user_id == user_id).first()
        if data:
            session.delete(data)
            session.commit()
            return True
        else:
            return False


class Like(Base):
    __tablename__ = 'likes'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)

    def __repr__(self):
        return '''
            <Like>++user_id={}, post_id={}
        '''.format(
            self.user_id,
            self.post_id
        )

    @classmethod
    def add_like(cls, user_id, post_id):
        """
        添加喜欢
        :param user_id:
        :param post_id:
        :return:
        """
        session.add(Like(user_id=user_id, post_id=post_id))
        session.commit()
        return True

    @classmethod
    def is_exits_like(cls, user_id, post_id):
        """
        添加喜欢之前先查找这个喜欢存不存在， 如果存在就删除
        :param user_id:
        :param post_id:
        :return:
        """
        data = session.query(cls).filter(cls.user_id == user_id, cls.post_id == post_id).first()
        return data

    @classmethod
    def del_like(cls, user_id, post_id):
        """
        再次点击红心 删除喜欢
        :param user_id:
        :param post_id:
        :return:
        """
        like = session.query(cls).filter(cls.user_id == user_id, cls.post_id == post_id).first()
        session.delete(like)
        session.commit()



if __name__ == '__main__':
    Base.metadata.create_all()