import random
import time

import redis

from library.cookie_pool.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


class RedisClient(object):
    def __init__(self, _type, website, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化Redis连接
        :param _type: 类型
        :param website: 网站
        :param host: 地址
        :param port: 端口
        :param password: 密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = _type
        self.website = website

    def name(self):
        """
        获取Hash的名称
        :return: Hash名称
        """
        return "{type}:{website}".format(type=self.type, website=self.website)

    def set(self, username, value):
        """
        设置键值对
        :param username: 用户名
        :param value: 密码或Cookies
        :return:
        """
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        """
        根据键名获取键值
        :param username: 用户名
        :return:
        """
        return self.db.hget(self.name(), username)

    def delete(self, username):
        """
        根据键名删除键值对
        :param username: 用户名
        :return: 删除结果
        """
        return self.db.hdel(self.name(), username)

    def count(self):
        """
        获取数目
        :return: 数目
        """
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        """
        val = self.db.hvals(self.name())    # []
        return random.choice(val) if val else ""

    def user_names(self):
        """
        获取所有账户信息
        :return: 所有用户名
        """
        return self.db.hkeys(self.name())

    def all(self):
        """
        获取所有键值对
        :return: 用户名和密码或Cookies的映射表
        """
        return self.db.hgetall(self.name())

    def lock(self, name, ex, nx=False, xx=False):
        """
        上锁
        :param xx: 已设置键才生效
        :param ex: 存在多少秒
        :param name: key
        :param nx: 未设置键才生效
        :return:
        """
        if isinstance(ex, tuple):
            ex = random.randint(*ex)
        key = f"{self.name()}:{name}"
        return self.db.set(key, "1", ex=ex, nx=nx, xx=xx)

    def frequency_limit(self, name: str, upper_limit: int, duration):
        """
        频率限制
        :param duration: 限制时长(秒)
        :param name: key
        :param upper_limit: 上限次数
        :return:
        """
        if callable(duration):
            _duration = int(duration())
        elif isinstance(duration, int):
            _duration = duration
        else:
            raise TypeError("The type of `duration` must be Callable or Int.")
        lock = f"{self.name()}:frequency:lock"
        while not self.db.set(lock, 1, ex=10, nx=True):      # 预防竞态条件
            time.sleep(1)
        key = f"{self.name()}:frequency:{name}"
        limit = self.db.get(key)       # 获取
        result = False
        if limit:
            if int(limit) < upper_limit:    # 限制次数小于上限
                self.db.incr(key)
                result = True
        else:
            if len(str(_duration)) >= 10:    # 大于等于10就理解为时间戳了
                self.db.set(key, 1)
                self.db.expireat(key, _duration)     # 赋初始值
            else:
                self.db.set(key, 1, ex=_duration)    # 赋初始值
            result = True
        self.db.delete(lock)
        return result


if __name__ == '__main__':
    pass
