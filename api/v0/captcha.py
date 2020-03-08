import io

from PIL import Image
from flask import request

from library.cnn_captcha.cnnlib.recognition_object import Recognizer
from library.cnn_captcha.settings import CAPTCHA_CONFIG
from library.redprint import RedPrint

api = RedPrint("captcha")
recognizer = Recognizer(
    CAPTCHA_CONFIG["image_height"],
    CAPTCHA_CONFIG["image_width"],
    CAPTCHA_CONFIG["max_captcha"],
    CAPTCHA_CONFIG["char_set"],
    CAPTCHA_CONFIG["model_save_dir"],
    "hb56.ckpt"
)


@api.route("/", methods=["GET"])
def get_captcha():
    """
    获取一张验证码图片
    :return:
    """
    return f'Params:{request.args}'


@api.route("/", methods=["POST"])
def read_captcha():
    """
    识别或上传一张验证码图片
    :return:
    """
    # 暂定：图片字段 img
    img = request.files.get("img")
    if img:
        img_bytes = io.BytesIO(img.stream.read())
        r_img = Image.open(img_bytes)
        text = recognizer.rec_image(r_img)
        return text
    return f"Data:{request.args}"
