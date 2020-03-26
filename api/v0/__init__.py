from flask import Blueprint

from api.v0.views import captcha
from api.v0.views import cookies


def create_blueprint():
    api_v0 = Blueprint("api", __name__)
    captcha.api.register(api_v0)
    cookies.api.register(api_v0)
    return api_v0
