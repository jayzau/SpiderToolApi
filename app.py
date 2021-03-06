from flask import Flask

from config.settings import FLASK_CONFIG


def register_blueprints(app):
    from api import create_blueprint
    from pages.views import pages

    app.register_blueprint(create_blueprint(), url_prefix="/api")
    app.register_blueprint(pages, url_prefix="/pages")


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


def create_database(app):
    from config.settings import SQLALCHEMY_CONFIG
    from api.models import db

    app.config.update(SQLALCHEMY_CONFIG)
    db.init_app(app)
    return app


def create_app():
    app = Flask(__name__, **FLASK_CONFIG)
    # 蓝图注册
    register_blueprints(app)
    # 异常处理
    app = err_handel(app)
    # 数据库注册
    app = create_database(app)
    return app


if __name__ == '__main__':
    pass
