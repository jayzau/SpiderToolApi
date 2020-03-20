from flask_rq2 import RQ

from library.cookie_pool.generator import *
from library.cookie_pool.tester import *
import time
from library.cookie_pool.settings import CYCLE, TESTER_MAP

rq = RQ()


@rq.job(func_or_queue="new_cookies")
def new_cookies(cls_name: str, _website: str, username: str, password: str):
    """
    异步登录账号，针对单个账号
    :param password:
    :param username:
    :param cls_name:
    :param _website:
    :return:
    """
    try:
        gen = eval(f"{cls_name}(website='{_website}')")     # 实例化
        gen.async_run(username, password)       # 调用登录方法
        del gen
    except Exception as e:
        print(e.args)


@rq.job(func_or_queue="new_cookies")
def check_cookies():
    try:
        total = len(TESTER_MAP)
        clear = 0
        job = get_current_job()
        for website, cls_name in TESTER_MAP.items():
            if job:
                job.meta["total"] = int(clear / total * 100)
            tester = eval(cls_name + '(website="' + website + '")')
            tester.run()
            del tester
            clear += 1
        if job:
            job.meta["total"] = int(clear / total * 100)
            print(job.meta)
        time.sleep(CYCLE)
    except Exception as e:
        print(e.args)


if __name__ == '__main__':
    pass
