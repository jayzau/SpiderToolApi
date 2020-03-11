from flask import request, jsonify

from library.cookie_pool.redis_cli import RedisClient
from library.cookie_pool.settings import TYPE_COOKIES, TYPE_ACCOUNTS, GENERATOR_MAP
from library.redprint import RedPrint

api = RedPrint("cookies")


@api.route("/<string:website>", methods=["GET"])
def get_cookie(website):
    """
    获取指定类型cookie
    :param website:
    :return:
    """
    if website:
        redis_cli = RedisClient(TYPE_COOKIES, website)
        cookie = redis_cli.random()
        return cookie
    return {}


@api.route("/count", methods=["GET"])
@api.route("/count/", methods=["GET"])
@api.route("/count/<string:website>", methods=["GET"])
def get_count(website=""):
    """
    获取账号与cookie的数量
    :param website:
    :return:
    """
    string = []
    if website:
        redis_cli_cookie = RedisClient(TYPE_COOKIES, website)
        redis_cli_account = RedisClient(TYPE_ACCOUNTS, website)
        cookie_count = redis_cli_cookie.count()
        account_count = redis_cli_account.count()
        string.append(f"{website}:{cookie_count}/{account_count}")
    else:
        for website in GENERATOR_MAP.keys():
            redis_cli_cookie = RedisClient(TYPE_COOKIES, website)
            redis_cli_account = RedisClient(TYPE_ACCOUNTS, website)
            cookie_count = redis_cli_cookie.count()
            account_count = redis_cli_account.count()
            string.append(f"{website}:{cookie_count}/{account_count}")
    return "<br>".join(string)


@api.route("", methods=["POST"])
def add_account():
    """
    新增账号
    :return:
    """
    website = request.form.get("website")
    account = request.form.get("account")
    password = request.form.get("password")
    if all([website, account, password]):       # 缺一不可
        if website not in GENERATOR_MAP.keys():        # 添加的账号所属网站还没有对应生成器
            result = {
                "status": 404,
                "content": "website err"
            }
        else:
            redis_cli = RedisClient(TYPE_ACCOUNTS, website)
            redis_cli.set(account, password)
            result = {
                "status": 200,
                "content": "ok"
            }
    else:
        result = {
            "status": 400,
            "content": "input err"
        }
    return jsonify(result)


@api.route("", methods=["DELETE"])
def del_account():
    """
    删除账号
    :return:
    """
    website = request.form.get("website")
    account = request.form.get("account")
    if all([website, account]):
        if website not in GENERATOR_MAP.keys():        # 添加的账号所属网站还没有对应生成器
            result = {
                "status": 404,
                "content": "website err"
            }
        else:
            redis_cli = RedisClient(TYPE_ACCOUNTS, website)
            redis_cli.delete(account)
            result = {
                "status": 200,
                "content": "ok"
            }
    else:
        result = {
            "status": 400,
            "content": "input err"
        }
    return jsonify(result)


@api.route("/accounts", methods=["GET"])
@api.route("/accounts/", methods=["GET"])
@api.route("/accounts/<string:website>", methods=["GET"])
def get_accounts(website=""):
    string = []
    if website:
        string.append(f"<h3>{website}</h3>")
        redis_cli = RedisClient(TYPE_ACCOUNTS, website)
        accounts = redis_cli.user_names()
        if accounts:
            string.append("<br>".join(accounts))
    else:
        for website in GENERATOR_MAP.keys():
            string.append(f"<h3>{website}</h3>")
            redis_cli = RedisClient(TYPE_ACCOUNTS, website)
            accounts = redis_cli.user_names()
            if accounts:
                string.append("<br>".join(accounts))
    return "<br>".join(string)
