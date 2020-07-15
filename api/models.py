from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Captcha(db.Model):
    __tablename__ = 'captcha'
    id = db.Column(db.Integer, primary_key=True)
    captcha_id = db.Column(db.String(81), nullable=False, comment='图片id')
    path = db.Column(db.String(256), nullable=False, comment='验证码地址')
    md5 = db.Column(db.String(81), nullable=False, comment='md5值')
    source = db.Column(db.String(24), nullable=False, comment='来源', default="super_me")
    timestamp = db.Column(db.Integer, index=True, default=int(datetime.now().timestamp()))

    def __repr__(self):
        return '<Captcha {}>'.format(self.id)

    @staticmethod
    def update():
        db.session.commit()


def add_and_commit(model):
    db.session.add(model)
    db.session.commit()
    return model.id


if __name__ == '__main__':
    from flask_migrate import Migrate, MigrateCommand
    from flask_script import Manager

    from flask import Flask
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from config.settings import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_BINDS

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    manage = Manager(app)
    migrate = Migrate(app, db)
    manage.add_command('db', MigrateCommand)

    manage.run()
    """
    init 
    migrate upgrade
    """
