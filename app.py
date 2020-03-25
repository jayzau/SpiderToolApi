from flask import Flask

from config.settings import REDIS_URL


def register_blueprints(app):
    from api.v0 import create_blueprint

    app.register_blueprint(create_blueprint(), url_prefix="/api_v0")


def register_rq(app):
    from library.async_rq2 import rq

    app.config['RQ_REDIS_URL'] = REDIS_URL
    rq.init_app(app)
    """
    工人启动 在根目录
    rq worker queue_name
    """
    return app


def err_handel(app):
    from werkzeug.exceptions import HTTPException
    from library.exceptions import ApiException

    @app.errorhandler(Exception)
    def framework_error(e):
        if isinstance(e, ApiException):
            return e
        if isinstance(e, HTTPException):
            code = e.code
            msg = e.description
            error_code = 1000
            return ApiException(code=code, msg=msg, error_code=error_code)
        else:
            if not app.config['DEBUG']:
                return ApiException()
            raise e
    return app


def create_app():
    app = Flask(__name__)
    # 蓝图注册
    register_blueprints(app)
    # 异常处理
    app = err_handel(app)
    # rq2异步任务注册
    app = register_rq(app)
    return app


if __name__ == '__main__':
    pass
