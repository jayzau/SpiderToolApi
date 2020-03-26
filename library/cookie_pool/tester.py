import json
import logging

import requests
from requests.cookies import RequestsCookieJar
from requests.exceptions import ConnectionError

from library.cookie_pool.redis_cli import RedisClient
from library.cookie_pool.request import request, TooManyRetries
from library.cookie_pool.settings import TEST_URL_MAP, TYPE_COOKIES, TYPE_ACCOUNTS


class ValidTester(object):
    logger = logging.getLogger("ValidTester")

    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient(TYPE_COOKIES, self.website)
        self.accounts_db = RedisClient(TYPE_ACCOUNTS, self.website)

    def test(self, username, cookies):
        raise NotImplementedError

    def del_cookie(self, username):
        self.cookies_db.delete(username)
        self.logger.info(f"{self.website:^10} | user:{username:<20} | Deleted.")

    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.items():
            self.logger.info(f"{self.website:^10} | user:{username:<20} | Test start.")
            self.test(username, cookies)
            self.logger.info(f"{self.website:^10} | user:{username:<20} | Test finished.")
            # time.sleep(10)


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
        del_flag = False
        try:
            cookie_list = json.loads(cookies)
            cookie_jar = RequestsCookieJar()
            for cookie in cookie_list:
                cookie_jar.set(name=cookie["name"], value=cookie["value"], domain=cookie["domain"], path=cookie["path"])
            response = request("GET", url=TEST_URL_MAP[self.website], cookies=cookie_jar, allow_redirects=False)
            if response.status_code == 200:
                self.logger.info(f"{self.website:^10} | user:{username:<20} | Online.")
            else:
                del_flag = True
                self.logger.info(f"{self.website:^10} | user:{username:<20} | Offline.")
        except (ValueError, KeyError):
            del_flag = True
            self.logger.info(f"{self.website:^10} | user:{username:<20} | Wrong type.")
        except TooManyRetries:
            self.logger.info(f"{self.website:^10} | user:{username:<20} | Network anomaly.")
        if del_flag:
            self.del_cookie(username)


if __name__ == '__main__':
    SipglValidTester("sipgl").run()
