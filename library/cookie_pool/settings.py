REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = None

CYCLE = 30
TYPE_COOKIES = "cookies"
TYPE_ACCOUNTS = "accounts"
TESTER_MAP = {
    "hb56": "Hb56ValidTester"
}
TEST_URL_MAP = {
    "hb56": "http://www.hb56.com/User/User.aspx"
}
GENERATOR_MAP = {
    "hb56": "Hb56CookiesGenerator",
    "hb57": "Hb56CookiesGenerator",
}
COOKIE_FREQUENCY_LIMIT = {          # cookie调用频率限制
    "hb56": 10
}
LOGIN_FREQUENCY_LIMIT = {           # 账号登录频率限制
    "hb56": 10
}

GENERATOR_PROCESS = True
VALID_PROCESS = True

