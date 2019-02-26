import hashlib
import os
from sql_dbs.connect import session
from sql_dbs.modules import User, Post, Like, Atte

'''login session'''
def hash_data(content):
    """
    用户密码加密方法
    :param content:
    :return:
    """
    return hashlib.md5(content.encode('utf8')).hexdigest()

def verify_login(username, password):
    """
    验证登陆方法
    :param username:
    :param password:
    :return:
    """
    # 查询数据库中是否存在用户
    info = User.search(username, hash_data(password))
    # 如果用户存在并且密码对了 就返回True
    if info and username == info.username and hash_data(password) == info.password:
        return True

    else:
        return False

def note_user(username, number, password, password1):
    """
    简单判断输入框中字段是否填写， 判断数据库中用户名是否存在， 并注册
    :param username:
    :param number:
    :param password:
    :param password1:
    :return:
    """
    msg = ''
    if username and number and password:
        # 判断用户名是否存在， 如果存在 则注册不成功
        if not User.is_exists(username):
            if password == password1:
                # 注册成功
                User.add_user(username, hash_data(password), number)
                session.commit()
            else:
                msg = 'password is not =='
                return msg
        else:
            msg = 'username is life'
            return msg
    else:
        msg = 'letter is not all'
        return msg

'''database session'''

def add_post_db(img_url, thumb_url, user_name):
    """
    将路径添加到post表中
    :param img_url:
    :param thumb_url:
    :param user_name:
    :return:
    """
    user = session.query(User.id).filter(User.username == user_name).first()
    post = Post(img_url=img_url, thumb_url=thumb_url, user_id=user.id)
    session.add(post)
    session.commit()
    # 返回post.id为了上传成功后直接跳到大图页
    return post

def search_post_for(username):
    """
    显示自己上传的大图index页面
    :param username:
    :return:
    """
    user = User.search_posts(username=username)
    if user:
        posts = user.post
        # 实现最新上传的图片在前
        posts.reverse()
        return posts
    else:
        return False

def search_all_thum():
    """
    查找所有的缩略图路径
    用order_by倒叙查询， 实现新上传的在前
    :return:
    """
    return session.query(Post).order_by(Post.id.desc()).all()

def get_post_id(post_id):
    """
    用于post路由获取post_id值
    :param post_id:
    :return:
    """
    return session.query(Post).filter(Post.id == post_id).first()

'''
添加喜欢图片到Like数据库
'''
def get_user(username):
    return session.query(User).filter(User.username == username).first()

def get_like_post(user):
    """
    查看用户喜欢的图片
    :param user:
    :return:
    """
    if user:
        # Like表的user_id代表哪一个用户， Like表的post_id代表喜欢哪一张图片， Like表的user_id不等于Post表的user_id 表示自己上传的不能喜欢
        # 要查询Post表  因为Post表有图片路径
        post = session.query(Post).filter(Like.user_id == user.id, Like.post_id == Post.id, Like.user_id != Post.user_id).all()
        post.reverse()
    else:
        post = []
    return post

def get_like_count(post):
    """
    统计post.id这张图片有多少人喜欢
    :param post:
    :return:
    """
    return session.query(Like).filter(Like.post_id == post.id).count()


def get_post(post_id):
    """
    获取post的id那条数据  用于删除本地图片
    :param post_id:
    :return:
    """
    return session.query(Post).filter(Post.id == post_id).first()

def del_upload_img(pid,   user_id):
    """
    删除自己上传的图片
    :param pid:
    :param user_id:
    :return:
    """
    post = get_post(pid)
    os.remove('static/{}'.format(post.img_url))
    os.remove('static/{}'.format(post.thumb_url))
    session.execute('DELETE FROM posts WHERE id={} AND user_id={}'.format(pid, user_id))
    session.commit()
    return True


def add_like(user_id, post_id):
    """
    添加喜欢
    :param user_id:
    :param post_id:
    :return:
    """
    session.add(Like(user_id=user_id, post_id=post_id))
    session.commit()
    return True


def is_exits_like(user_id, post_id):
    """
    添加喜欢之前先查找这个喜欢存不存在， 如果存在就删除
    :param user_id:
    :param post_id:
    :return:
    """
    data = session.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    return data


def del_like(user_id, post_id):
    """
    再次点击红心 删除喜欢
    :param user_id:
    :param post_id:
    :return:
    """
    like = session.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    session.delete(like)
    session.commit()



def add_atte(m_id, y_id):
    """
    添加关注
    :param m_id: 关注人
    :param y_id: 被关注人
    :return:
    """
    data = Atte(m_id=m_id, y_id=y_id)
    session.add(data)
    session.commit()
    return True


def atte_is_exits(m_id, y_id):
    """
    判断关注  是否已经关注了 如果关注就返回数据  如果没关注就返回None
    :param m_id:
    :param y_id:
    :return:
    """
    return session.query(Atte).filter(Atte.m_id == m_id, Atte.y_id == y_id).first()


def delete_atte(m_id, y_id):
    """
    删除关注用户
    :param m_id:
    :param y_id:
    :return:
    """
    data = session.query(Atte).filter(Atte.m_id == m_id, Atte.y_id == y_id).first()
    session.delete(data)
    session.commit()
    return True