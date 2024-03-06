import hashlib

from django.conf import settings


def toMd5(str):
    """加盐MD5"""
    m = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    m.update(str.encode("utf8"))
    return m.hexdigest()