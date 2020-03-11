import random

from flask import request, jsonify

from api.v0.enums import Status
from api.v0.forms import AddAccountForm, DelAccountForm
from library.cookie_pool.redis_cli import RedisClient
from library.cookie_pool.settings import TYPE_COOKIES, TYPE_ACCOUNTS, GENERATOR_MAP, COOKIE_FREQUENCY_LIMIT
from library.redprint import RedPrint

api = RedPrint("cookies")


@api.route("/<string:website>", methods=["GET"])
def get_cookie(website):
    """
    获取指定类型cookie
    :param website:
    :return:
    """
    cookie = ""
    status = Status.success.value
    if website:
        redis_cli = RedisClient(TYPE_COOKIES, website)
        times = COOKIE_FREQUENCY_LIMIT.get(website)
        if times:
            cookies = redis_cli.all()
            if cookies:
                while cookies and not cookie:
                    cookie_keys = list(cookies.keys())
                    account = random.choice(cookie_keys)
                    if redis_cli.lock(account, times):      # 上锁成功
                        cookie = cookies[account]
                        break
                    else:       # 冷却期 暂不可用
                        del cookies[account]
                else:   # 便利完了还没找到可用的
                    status = Status.busy.value
        else:       # 无频率限制 随机取一个即可
            cookie = redis_cli.random()

    return jsonify({
        "status": status,
        "cookie": cookie,
    })


@api.route("/count/", methods=["GET"])
@api.route("/count/<string:website>", methods=["GET"])
def get_count(website=""):
    """
    获取账号与cookie的数量
    :param website:
    :return:
    """
    def get_result(_website):
        redis_cli_cookie = RedisClient(TYPE_COOKIES, _website)
        redis_cli_account = RedisClient(TYPE_ACCOUNTS, _website)
        _cookie_count = redis_cli_cookie.count()
        _account_count = redis_cli_account.count()
        return {
            "website": _website,
            "cookie_count": _cookie_count,
            "account_count": _account_count,
        }
    details = []
    if website:
        details.append(get_result(website))
    else:
        for website in GENERATOR_MAP.keys():
            details.append(get_result(website))
    status = Status.success.value
    return jsonify({
        "status": status,
        "details": details
    })


@api.route("", methods=["POST"])
def add_account():
    """
    新增指定账号
    :return:
    """
    form = AddAccountForm(request.form)
    if form.validate():
        redis_cli = RedisClient(TYPE_ACCOUNTS, form.website.data)
        redis_cli.set(form.account.data, form.password.data)
        status = Status.success.value
    else:
        status = Status.input_err.value
    error_str = form.errors
    return jsonify({
        "status": status,
        "error_str": error_str
    })


@api.route("", methods=["DELETE"])
def del_account():
    """
    删除指定账号
    :return:
    """
    form = DelAccountForm(request.form)
    if form.validate():
        redis_cli = RedisClient(TYPE_ACCOUNTS, form.website.data)
        redis_cli.delete(form.account.data)
        status = Status.success.value
    else:
        status = Status.input_err.value
    error_str = form.errors
    return jsonify({
        "status": status,
        "error_str": error_str
    })


@api.route("/accounts/", methods=["GET"])
@api.route("/accounts/<string:website>", methods=["GET"])
def get_accounts(website=""):
    """
    获取账号名和数量
    :param website: 选择网站，空为全选
    :return:
    """
    def get_result(_website):
        redis_cli = RedisClient(TYPE_ACCOUNTS, _website)
        _accounts = redis_cli.user_names()
        return {
            "website": _website,
            "accounts": _accounts,
            "amount": len(_accounts),
        }
    details = []
    if website:
        details.append(get_result(website))
    else:
        for website in GENERATOR_MAP.keys():
            details.append(get_result(website))
    status = Status.success.value
    return jsonify({
        "status": status,
        "details": details
    })
