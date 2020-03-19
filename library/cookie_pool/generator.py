import json
from random import randint

import requests

from library.cookie_pool.request import request
from library.cookie_pool.redis_cli import RedisClient
from library.cookie_pool.settings import LOGIN_FREQUENCY_LIMIT, LOGIN_DEFAULT_FREQUENCY_LIMIT, LOGIN_LOCK_KEY


class CookiesGenerator(object):
    def __init__(self, website='default'):
        """
        父类, 初始化一些对象
        :param website: 名称
        """
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
        wait_time = LOGIN_FREQUENCY_LIMIT.get(website) or LOGIN_DEFAULT_FREQUENCY_LIMIT
        self.wait_time = wait_time
        if wait_time:
            if isinstance(wait_time, tuple):
                self.wait_time = randint(*wait_time)

    def __del__(self):
        pass

    def new_cookies(self, username, password):
        """
        新生成Cookies，子类需要重写
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def process_cookies(cookies):
        """
        处理Cookies
        :param cookies:
        :return:
        """
        lst = []
        for cookie in cookies:
            lst.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain
            })
        return lst

    def async_run(self, username, password):
        """
        只处理一个账号的登录 方便外部异步处理
        :param username:
        :param password:
        :return:
        """
        if self.accounts_db.lock(LOGIN_LOCK_KEY, self.wait_time, xx=True):
            # 在任务提交范围时间内才执行 超时说明worker数量不够 任务执行过于缓慢
            result = self.new_cookies(username, password)
            # 成功获取
            if result.get('status') == 1:
                cookies = self.process_cookies(result.get('cookies'))
                print(f'{username} 成功获取到Cookies', cookies)
                if self.cookies_db.set(username, json.dumps(cookies)):
                    print(f'{username} 成功保存Cookies')
            # 密码错误，移除账号
            elif result.get('status') == 2:
                print(result.get('content'))
                if self.accounts_db.delete(username):
                    print(f'密码错误，删除账号 {username}')
            elif result.get('status') == -1:
                if self.accounts_db.delete(username):
                    print(f'账号失效，删除账号 {username}')
            else:
                print(result.get('content'))
        else:
            print(f"{username} 任务超时，取消执行")


class Hb56CookiesGenerator(CookiesGenerator):
    def __init__(self, website='hb56'):
        """
        初始化操作
        :param website: 站点名称
        """
        CookiesGenerator.__init__(self, website)
        self.website = website

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        return {}


class SipglCookiesGenerator(CookiesGenerator):
    def __int__(self, website="sipgl"):
        CookiesGenerator.__init__(self, website)

    def new_cookies(self, username, password):
        session = requests.Session()
        host = "cx.sipgl-fa.com:81"
        own_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36'
        }
        """获取cookie"""
        url = 'http://www.sipgl-fa.com/'
        request("GET", url=url, session=session, headers=own_headers)
        """获取验证码"""
        pic_headers = {
            'Referer': 'http://www.sipgl-fa.com/'
        }
        pic_headers.update(own_headers)
        url = f'http://{host}/sipgl-fa/login/img'
        res = request("GET", url=url, session=session, headers=pic_headers)
        status_code = res.status_code
        if status_code != 200:
            res = request("GET", url=url, session=session, headers=pic_headers)
        pic = res.content

        pic_str = request("POST", url="http://101.200.120.188/api_v0/captcha/", files={"img": pic}).text
        if not pic_str:
            pic_str = request("POST", url="http://101.200.120.188/api_v0/captcha/", files={"img": pic}).text

        if pic_str:
            """登录并验证"""
            url = f'http://{host}/sipgl-fa/login/lgnNew.json'
            data = {
                'laccount': 'guest',
                'lpawword': 'guest',
                'lauthcode': f'{pic_str}'
            }
            r = request("POST", url=url, session=session, headers=pic_headers, data=data)
            if 'errorCode:1' in r.text:
                if res:
                    pass
        cookies = session.cookies
        session.close()
        return {
            "status": 1,
            "cookies": cookies,
            "content": ""
        }


if __name__ == '__main__':
    pass
