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
        session.add(User(username=username, password=password, number=number))
        session.commit()

    @classmethod
    def search(cls, username, password):
        return session.query(User).filter(User.username == username, User.password == password).first()

    @classmethod
    def is_exists(cls, username):
        return session.query(User).filter(exists().where(User.username == username)).first()

    @classmethod
    def search_posts(cls, username):
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
        session.add(Like(user_id=user_id, post_id=post_id))
        session.commit()
        return True

    @classmethod
    def is_exits_like(cls, user_id, post_id):
        data = session.query(cls).filter(cls.user_id == user_id, cls.post_id == post_id).first()
        return data

    @classmethod
    def del_like(cls, user_id, post_id):
        like = session.query(cls).filter(cls.user_id == user_id, cls.post_id == post_id).first()
        session.delete(like)
        session.commit()

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(30), nullable=True)
    create_time = Column(DateTime, default=datetime.now)
    article_user = relationship('User', backref='articles', secondary='user_article')

    def __repr__(self):
        return '''
            <Article>++id={}, content={}, create_time={}
        '''.format(
            self.id,
            self.content,
            self.create_time
        )


user_articles = Table('user_article', Base.metadata,
                      Column('user_id', Integer, ForeignKey('user.id')),
                      Column('article_id', Integer, ForeignKey('article.id'))
                      )




if __name__ == '__main__':
    Base.metadata.create_all()