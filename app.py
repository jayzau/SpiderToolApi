from flask import Flask

from api.v0 import create_blueprint
from config.settings import REDIS_URL
from library.async_rq2 import rq


def register_blueprints(app):
    app.register_blueprint(create_blueprint(), url_prefix="/api_v0")


def register_rq(app):
    app.config['RQ_REDIS_URL'] = REDIS_URL
    rq.init_app(app)
    """
    工人启动 在根目录
    rq worker queue_name
    """
    return app


def create_app():
    app = Flask(__name__)
    # 蓝图注册
    register_blueprints(app)
    # rq2异步任务注册
    app = register_rq(app)
    return app


if __name__ == '__main__':
    pass
