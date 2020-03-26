import random

from flask import request, jsonify

from api.v0.enums import ResponseCode
from api.v0.forms import AddAccountForm, DelAccountForm
from library.cookie_pool.redis_cli import RedisClient
from library.async_rq2 import new_cookies, check_cookies
from library.cookie_pool.settings import TYPE_COOKIES, TYPE_ACCOUNTS, GENERATOR_MAP, COOKIE_FREQUENCY_LIMIT, \
    LOGIN_TASK_WAITING_TIME, LOGIN_LOCK_KEY
from library.pub_func import login_lock_key
from library.redprint import RedPrint

api = RedPrint("cookies")


@api.route("/<string:website>", methods=["GET"])
def get_cookie(website):
    """
    获取指定类型cookie
    新需求：
        某网站单个账号限制查询次数/天 得做一定限制
    :param website:
    :return:
    """
    cookie = ""
    status = ResponseCode.SUCCESS.value
    if website:
        redis_cli = RedisClient(TYPE_COOKIES, website)
        times = COOKIE_FREQUENCY_LIMIT.get(website)
        if isinstance(times, int):
            cookies = redis_cli.all()
            while cookies and not cookie:
                cookie_keys = list(cookies.keys())
                account = random.choice(cookie_keys)
                if redis_cli.lock(account, times, nx=True):      # 上锁成功
                    cookie = cookies[account]
                    break
                else:       # 冷却期 暂不可用
                    del cookies[account]
            else:   # 便利完了还没找到可用的
                status = ResponseCode.BUSY.value
        elif isinstance(times, tuple):
            cookies = redis_cli.all()
            while cookies and not cookie:
                cookie_keys = list(cookies.keys())
                account = random.choice(cookie_keys)
                if redis_cli.frequency_limit(account, *times):      # 上锁成功
                    cookie = cookies[account]
                    break
                else:       # 冷却期 暂不可用
                    del cookies[account]
            else:   # 便利完了还没找到可用的
                status = ResponseCode.BUSY.value
        else:       # 无频率限制 随机取一个即可
            cookie = redis_cli.random()

    return jsonify({
        "error_code": status,
        "msg": "",
        "data": cookie,
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
    status = ResponseCode.SUCCESS.value
    return jsonify({
        "error_code": status,
        "msg": "",
        "data": details
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
        status = ResponseCode.SUCCESS.value
    else:
        status = ResponseCode.INPUT_ERR.value
    return jsonify({
        "error_code": status,
        "msg": form.errors
    })


@api.route("", methods=["DELETE"])
def del_account():
    """
    删除指定账号
    :return:
    """
    form = DelAccountForm(request.form)
    if form.validate():
        # 先将对应cookie也应该删一次
        redis_cli_cookies = RedisClient(TYPE_COOKIES, form.website.data)
        redis_cli_cookies.delete(form.account.data)
        # 再删除账号
        redis_cli_accounts = RedisClient(TYPE_ACCOUNTS, form.website.data)
        redis_cli_accounts.delete(form.account.data)
        status = ResponseCode.SUCCESS.value
    else:
        status = ResponseCode.INPUT_ERR.value
    return jsonify({
        "error_code": status,
        "msg": form.errors
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
    status = ResponseCode.SUCCESS.value
    return jsonify({
        "error_code": status,
        "msg": "",
        "data": details
    })


@api.route("/check_cookie_status/", methods=["GET"])
def check_cookie_status():
    """
    检测哪些账号没有cookie 检测完毕之后提交重新登录 暂定
    下一步计划：
        增加账号数量控制，数量低于某个值，自动从相应地方提取填充
        增加账号登录次数限制，比如某个账号单位时间内登录次数过多，邮箱提醒管理员进行处理
    :return:
    """
    job_ids = []
    for website, cls_name in GENERATOR_MAP.items():
        cookies_db = RedisClient('cookies', website)
        accounts_db = RedisClient('accounts', website)

        accounts_user_names = accounts_db.user_names()
        cookies_user_names = cookies_db.user_names()

        for username in accounts_user_names:
            # 遍历账号 查看有没有cookie
            if username in cookies_user_names:      # cookie还存在 有效性不在这里检测
                pass
            elif accounts_db.lock(login_lock_key(LOGIN_LOCK_KEY, website, username), LOGIN_TASK_WAITING_TIME, nx=True):
                # 这里要处理一下是否重复提交
                password = accounts_db.get(username)
                job = new_cookies.queue(cls_name, website, username, password)
                job_ids.append(job.get_id())
            else:       # 任务已经提交过，但还未做处理/登录冷却期 避免重复提交
                pass
    return jsonify({
        "error_code": ResponseCode.SUCCESS.value,
        "msg": "",
        "data": job_ids
    })


@api.route("/check_cookie_validity/", methods=["GET"])
def check_cookie_validity():
    """
    检测cookie是否还有效
    下一步计划:
        根据不同网站的cookie 制定不同的检测时间间隔
    :return:
    """
    job = check_cookies.queue()
    return {
        "error_code": ResponseCode.SUCCESS.value,
        "msg": "",
        "data": job.get_id()
    }
