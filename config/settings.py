import os

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'password': None,
    'db': 0,
    'decode_responses': True
}
REDIS_URL = "redis://{host}:{port}/{db}".format(
    host=REDIS_CONFIG["host"], port=REDIS_CONFIG["port"], db=REDIS_CONFIG["db"])

MYSQL_CONFIG = {
    'database': 'xkkweb',
    'user': 'jayzau',
    'password': '123456',
    'host': 'localhost',
    'port': 3306
}
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}/{database}"\
    .format(
        user=MYSQL_CONFIG["user"], password=MYSQL_CONFIG["password"],
        host=MYSQL_CONFIG["host"], database=MYSQL_CONFIG["database"]
    )
# SQLALCHEMY_BINDS = {
#     "db": "mysql+pymysql://{user}:{password}@{host}/{database}".format(
#         user=MYSQL_CONFIG["user"], password=MYSQL_CONFIG["password"],
#         host=MYSQL_CONFIG["host"], database="db"
#     )
# }
SQLALCHEMY_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
    # "SQLALCHEMY_BINDS": SQLALCHEMY_BINDS,
    "SQLALCHEMY_COMMIT_ON_TEARDOWN": True,
    "SQLALCHEMY_ECHO": False,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}

LOGGING_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
DEBUG = False

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLASK_CONFIG = dict(
    static_folder="static",
    template_folder="templates"
)
APP_CONFIG = dict(
    host="0.0.0.0",
    port=7118,
    debug=DEBUG
)

