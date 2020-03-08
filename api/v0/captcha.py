from flask import request

from library.redprint import RedPrint

api = RedPrint("captcha")


@api.route("/", methods=["GET"])
def get_captcha():
    """
    获取一张验证码图片
    :return:
    """
    return f'Params:{request.args}'


@api.route("/", methods="POST")
def read_captcha():
    """
    识别或上传一张验证码图片
    :return:
    """
    return f"Data:{request.args}"
