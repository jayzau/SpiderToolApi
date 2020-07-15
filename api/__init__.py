from flask import Blueprint

from api.views import captcha


def create_blueprint():
    api = Blueprint("api", __name__)
    captcha.api.register(api)
    return api
