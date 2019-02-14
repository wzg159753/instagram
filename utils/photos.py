import os
import uuid
from PIL import Image



# def save_upload(name, content):
#     with open('static/uploads/{}'.format(name), 'wb') as f:
#         f.write(content)
#     return 'uploads/{}'.format(name)
#
# def save_suo(name, size):
#     img, sei = os.path.splitext(name)
#     im = Image.open('static/uploads/{}'.format(name))
#     im.thumbnail(size)
#     im.save('static/suo/{}_{}x{}{}'.format(img, size[0], size[1], sei))
#     return 'suo/{}_{}x{}{}'.format(img, size[0], size[1], sei)


class UploadImage(object):

    upload_dir = 'uploads'
    suo_dir = 'suo'
    size = (200, 200)

    def __init__(self, username, static):
        self.name = username
        self.static = static
        self.newname = self.get_only_name(username)

    def get_only_name(self, username):
        name, sem = os.path.splitext(username)
        new_name = uuid.uuid4().hex
        return new_name + sem

    @property
    def get_upload_path(self):
        return os.path.join(self.upload_dir, self.newname)

    @property
    def get_static_upload(self):
        return os.path.join(self.static, self.get_upload_path)

    def save_upload(self, content):
        with open(self.get_static_upload, 'wb') as f:
            f.write(content)

    @property
    def get_thumb_path(self):
        name, sem = os.path.splitext(self.newname)
        new_name = '{}_{}x{}{}'.format(name, self.size[0], self.size[1], sem)
        return os.path.join(self.suo_dir, new_name)

    @property
    def get_static_thumb(self):
        return os.path.join(self.static, self.get_thumb_path)

    def save_thumb(self):
        im = Image.open(self.get_static_upload)
        im.thumbnail(self.size)
        im.save(self.get_static_thumb)
