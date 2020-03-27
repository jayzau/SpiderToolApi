import logging
from functools import partial

from library.pub_func import timedelta_ts

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = None

CYCLE = 30
TYPE_COOKIES = "cookies"
TYPE_ACCOUNTS = "accounts"
TESTER_MAP = {
    # "hb56": "Hb56ValidTester",
    "sipgl": "SipglValidTester"
}
TEST_URL_MAP = {
    "hb56": "http://www.hb56.com/User/User.aspx",
    "sipgl": "http://cx.sipgl-fa.com:81/sipgl-fa/biz/SearchByBillno.jsp?appid=116&cnbillno=&token=379"
}
GENERATOR_MAP = {
    # "hb56": "Hb56CookiesGenerator",
    "sipgl": "SipglCookiesGenerator"
}
COOKIE_FREQUENCY_LIMIT = {          # cookie调用频率限制
    "hb56": 10,          # 间隔多少秒可使用一次
    "sipgl": (50, partial(timedelta_ts, **{"minutes": 10}))        # 十分钟50次使用限制
}

LOGIN_LOCK_KEY = "login:lock:"
LOGIN_TASK_WAITING_TIME = 600      # 任务提交后的等待时间/入队后等待过期时间 十分钟内应当处理
LOGIN_DEFAULT_FREQUENCY_LIMIT = 30        # 给个时间差容错/登录需要时间
LOGIN_FREQUENCY_LIMIT = {           # 账号登录频率限制
    "hb56": (1800, 3600)
}

GENERATOR_PROCESS = True
VALID_PROCESS = True


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
)
