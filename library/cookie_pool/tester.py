import json
import time

import requests
from requests.cookies import RequestsCookieJar
from requests.exceptions import ConnectionError
from rq import get_current_job

from library.cookie_pool.redis_cli import RedisClient
from library.cookie_pool.request import request, TooManyRetries
from library.cookie_pool.settings import TEST_URL_MAP


class ValidTester(object):
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)

    def test(self, username, cookies):
        raise NotImplementedError

    def run(self):
        cookies_groups = self.cookies_db.all()
        job = get_current_job()
        website = len(cookies_groups)
        clear = 0
        for username, cookies in cookies_groups.items():
            if job:
                job.meta["website"] = int(clear / website * 100)
                print(job.meta)
            self.test(username, cookies)
            time.sleep(10)
            clear += 1
        if job:
            job.meta["website"] = int(clear / website * 100)
            print(job.meta)


class Hb56ValidTester(ValidTester):
    def __init__(self, website='hb56'):
        ValidTester.__init__(self, website)

    def test(self, username, cookies):
        print('正在测试Cookies', '用户名', username)
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies不合法', username)
            self.cookies_db.delete(username)
            print('删除Cookies', username)
            return
        try:
            test_url = TEST_URL_MAP[self.website]
            response = requests.get(test_url, cookies=cookies, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print('Cookies有效', username)
            else:
                print(response.status_code, response.headers)
                print('Cookies失效', username)
                self.cookies_db.delete(username)
                print('删除Cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


class SipglValidTester(ValidTester):
    def __int__(self, website="sipgl"):
        ValidTester.__init__(self, website)

    def test(self, username, cookies):
        # print(f"Cookie测试 | source:{self.website} | user:{username}")
        del_flag = False
        try:
            cookie_list = json.loads(cookies)
            cookie_jar = RequestsCookieJar()
            for cookie in cookie_list:
                cookie_jar.set(name=cookie["name"], value=cookie["value"], domain=cookie["domain"])
            response = request("GET", url=TEST_URL_MAP[self.website], cookies=cookie_jar, allow_redirects=False)
            if response.status_code == 200:
                # print(f"Cookie有效 | source:{self.website} | user:{username}")
                pass
            else:
                del_flag = True
                # print(f"Cookie失效 | source:{self.website} | user:{username}")
        except (ValueError, KeyError):
            del_flag = True
            # print(f"Cookie格式有误 | source:{self.website} | user:{username}")
        except TooManyRetries:
            # print(f"Cookie测试失败 | source:{self.website} | user:{username}")
            pass
        if del_flag:
            self.cookies_db.delete(username)
            # print(f"已删除Cookie | source:{self.website} | user:{username}")


if __name__ == '__main__':
    SipglValidTester().run()
