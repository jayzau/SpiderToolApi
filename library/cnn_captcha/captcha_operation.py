import datetime
import hashlib
from random import randint

from library.cnn_captcha.settings import DEFAULT_WEBSITE, DEFAULT_MAX_CAPTCHA, DEFAULT_CHAR_SET, DEFAULT_IMAGE_SUFFIX


def create_pic_id():
    """
    验证码id生成
    :return:
    """
    timestamp = str(int(datetime.datetime.now().timestamp() * 100000))
    rd = randint(100, 999)
    return int(f"{timestamp[5:10]}{rd}{timestamp[:5]}{timestamp[10:]}")


def md5_encode(s) -> str:
    """
    计算 MD5
    :param s:
    :return:
    """
    md5 = hashlib.md5()
    if isinstance(s, str):
        s = s.encode(encoding='utf-8')
    md5.update(s)
    return md5.hexdigest()


def make_recognizer_key(website, max_captcha, char_set):
    return f"{website}:{max_captcha}:{char_set}"


def parse_recognizer_key(recognizer_key: str):
    try:
        website, max_captcha, char_set = recognizer_key.split(":")
    except ValueError:
        website, max_captcha, char_set = DEFAULT_WEBSITE, DEFAULT_MAX_CAPTCHA, DEFAULT_CHAR_SET
    return website, int(max_captcha), char_set


def make_pic_name(recognizer_key, md5, pic_str=""):
    if pic_str:
        return f"{recognizer_key}_{md5}_{pic_str}.{DEFAULT_IMAGE_SUFFIX}"
    return f"{recognizer_key}_{md5}.{DEFAULT_IMAGE_SUFFIX}"


def parse_pic_name(pic_name):
    keys = pic_name.split(".")[0].split("_")
    if len(keys) < 3:
        recognizer_key, md5 = keys
        pic_str = ""
    else:
        recognizer_key, md5, pic_str = keys
    return recognizer_key, md5, pic_str


def make_pic_name_for_train(captcha_str):
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    return f"{captcha_str}_{timestamp}.{DEFAULT_IMAGE_SUFFIX}"


if __name__ == '__main__':
    print(create_pic_id())
