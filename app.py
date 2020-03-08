from flask import Flask

from api.v0 import create_blueprint


def register_blueprints(app):
    app.register_blueprint(create_blueprint(), url_prefix="/api_v0")


def create_app():
    app = Flask(__name__)
    # 蓝图注册
    register_blueprints(app)
    return app


if __name__ == '__main__':
    pass
