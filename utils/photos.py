import os
import glob
from PIL import Image


def save_upload(name, content):
    with open('static/uploads/{}'.format(name), 'wb') as f:
        f.write(content)

def save_suo(name, size):
    img, sei = os.path.splitext(name)
    im = Image.open('static/uploads/{}'.format(name))
    im.thumbnail(size)
    im.save('static/uploads/suo/{}_{}x{}{}'.format(img, size[0], size[1], sei), 'JPEG')