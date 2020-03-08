from flask import Blueprint

from api.v0 import captcha


def create_blueprint():
    api_v0 = Blueprint("api", __name__)
    captcha.api.register(api_v0)
    return api_v0
