"""
图片识别 把三方识别和自家识别糅合到一起
"""
import io
import os
from functools import partial

import requests
from PIL import Image

from library.cnn_captcha.cnnlib.recognition_object import Recognizer
from library.cnn_captcha.settings import CAPTCHA_CONFIG, CHAR_SET, SOFT_ID, IMAGE_HEIGHT, IMAGE_WIDTH, DEFAULT_CHAR_SET
from library.cnn_captcha.captcha_operation import md5_encode, make_recognizer_key, parse_recognizer_key

# 根据已有的模型创建对应类
recognizers = {}
metas = [i for i in os.listdir(CAPTCHA_CONFIG["model_save_dir"]) if i.endswith("meta")]
base_config = dict(
    image_height=IMAGE_HEIGHT,  # 图片高度
    image_width=IMAGE_WIDTH,  # 图片宽度
    model_save_dir=CAPTCHA_CONFIG["model_save_dir"],  # 保存路径
)
base_rec = partial(Recognizer, **base_config)

for meta in metas:
    model_save_name = meta.replace(".meta", "")
    _recognizer_key = meta.replace(".ckpt.meta", "")
    _, _max_captcha, _char_set = parse_recognizer_key(_recognizer_key)
    if not _max_captcha:
        _max_captcha = CAPTCHA_CONFIG["max_captcha"]
    if not _char_set:
        _char_set_value = CHAR_SET[DEFAULT_CHAR_SET]
    else:
        _char_set_value = CHAR_SET.get(_char_set)
        if not _char_set_value:
            _char_set_value = CHAR_SET[DEFAULT_CHAR_SET]
    recognizers[_recognizer_key] = base_rec(
        model_save_name=model_save_name,
        max_captcha=_max_captcha,
        char_set=_char_set_value,
    )

"""这里是自家图片识别的逻辑代码 以超级鹰为参考"""


def parse_img_code(
        img_bytes,
        website, max_captcha, char_set,
        username, password, soft_id, code_type=1902
):
    # recognizer_key = f"{website}:{max_captcha}:{char_set}"
    recognizer_key = make_recognizer_key(website, max_captcha, char_set)
    recognizer = recognizers.get(recognizer_key)
    if all([
        username,
        password,
        soft_id,
        code_type
    ]):   # 在不够信任自家打码正确率的时候 优先利用三方打码平台去识别 识别出来的结果用于自己训练
        json_data = sp_parse_img_code(img_bytes, username, password, soft_id, code_type)
        pic_str = json_data.get("pic_str")
        pic_id = int(json_data.get("pic_id") or "0")  # 自家用的是int类型
        md5 = json_data.get("md5")
        source = "super_eagle"
    elif recognizer:    # 自己打码
        img = io.BytesIO(img_bytes)
        r_img = Image.open(img)
        pic_str = recognizer.rec_image(r_img)
        # pic_id = create_pic_id()
        pic_id = ""
        md5 = md5_encode(img_bytes)
        source = "super_me"
    else:   # 新图片
        pic_str = ""
        # pic_id = create_pic_id()
        pic_id = ""
        md5 = md5_encode(img_bytes)
        source = "super_me"
    return {
        "recognizer_key": recognizer_key,
        "pic_str": pic_str,
        "pic_id": pic_id,
        "md5": md5,
        "source": source,
    }


"""下面为超级鹰的接口"""


def sp_parse_img_code(img, username, password, soft_id, code_type=1902) -> dict:
    """
    题目类型 参考 http://www.chaojiying.com/price.html
    :param soft_id: 软件id
    :param password: 密码
    :param username: 账号
    :param img: 图片流
    :param code_type: 验证码类型
    :return: {"err_no":0,"err_str":"OK","pic_id":"1662228516102","pic_str":"8vka","md5":"..."}
    """
    with requests.Session() as sess:
        data = {
            'user': username,
            'pass2': md5_encode(password),
            'softid': SOFT_ID.get(soft_id) or soft_id,
            'codetype': str(code_type)
        }
        files = {'userfile': ('ccc.jpg', img)}
        url = 'http://upload.chaojiying.net/Upload/Processing.php'
        resp = sess.post(url=url, data=data, files=files)
        json_data = resp.json()
        if json_data.get('err_no') == -10052:
            """超级鹰包月过期"""
            pass
        elif json_data.get('err_no') == -3002:
            pass
        return json_data


def sp_report_error(pic_id, username, password, soft_id):
    """
    反馈错误
    :param soft_id:
    :param password:
    :param username:
    :param pic_id: 报错题目的图片ID
    :return:
    """
    if pic_id:
        with requests.Session() as sess:
            data = {
                'user': username,
                'pass2': md5_encode(password),
                'softid': SOFT_ID.get(soft_id) or soft_id,
                'id': pic_id,
            }
            url = 'http://upload.chaojiying.net/Upload/ReportError.php'
            resp = sess.post(url=url, data=data)
            return resp.json()


