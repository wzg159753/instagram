import hashlib
from sql_dbs.connect import session
from sql_dbs.modules import User, Post


'''login session'''
def hash_data(content):
    return hashlib.md5(content.encode('utf8')).hexdigest()

def verify_login(username, password):
    info = User.search(username, hash_data(password))
    if info and username == info.username and hash_data(password) == info.password:
        return True

    else:
        return False

def note_user(username, number, password, password1):
    msg = ''
    if username and number and password:
        if not User.is_exists(username):
            if password == password1:
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
    user = session.query(User.id).filter(User.username == user_name).first()
    post = Post(img_url=img_url, thumb_url=thumb_url, user_id=user.id)
    session.add(post)
    session.commit()
    return post.id

def search_post_for(username):
    user = User.search_posts(username=username)
    if user:
        return user.post
    else:
        return False

def search_all_thum():
    return session.query(Post).all()

def get_post_id(post_id):
    return session.query(Post).filter(Post.id == post_id).first()



