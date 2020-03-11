"""
自定义网络请求
"""
import functools
from concurrent.futures import wait, ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ReadTimeout, ConnectTimeout, ConnectionError

timeout = (5, 10)
pool_connections = 30
pool_maxsize = 30
# 代理错误返回文本
proxy_error_text = [
    'The requested URL could not be retrieved',
    '您所请求的网址（URL）无法获取',
    'www.moguproxy.com'         # 蘑菇代理的网址
]


class TooManyRetries(requests.exceptions.RetryError):
    pass


def get_proxy():
    return {}


def request(method, url, session: requests.Session = None, proxy_enable=True, **kwargs):
    """
    单次请求
    :param method:
    :param url:
    :param session:
    :param proxy_enable:
    :param kwargs:
    :return:
    """
    if "timeout" not in kwargs:
        kwargs["timeout"] = timeout
    if proxy_enable:
        kwargs["proxies"] = get_proxy() or {}
    if "headers" not in kwargs:
        kwargs["headers"] = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/73.0.3683.86 Safari/537.36"}
    retry = 3
    while retry:
        try:
            if session:
                session.mount('https://', HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize))
                session.mount('http://', HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize))
                response = session.request(method=method, url=url, **kwargs)
            else:
                response = requests.request(method=method, url=url, **kwargs)
            content_type = response.headers.get('Content-Type')
            if content_type and 'text' in content_type:
                html = response.text
                if any([text in html for text in proxy_error_text]):
                    raise ProxyError(proxy_error_text)
            return response
        except ReadTimeout:
            print(f"读取超时 | method:{method} | proxies:{kwargs.get('proxies')} | url:{url}")
        except ProxyError:
            print(f"代理失效 | method:{method} | proxies:{kwargs.get('proxies')} | url:{url}")
        except ConnectTimeout:
            print(f"连接超时 | method:{method} | proxies:{kwargs.get('proxies')} | url:{url}")
        except ConnectionError:
            print(f"连接错误 | method:{method} | proxies:{kwargs.get('proxies')} | url:{url}")
        except Exception as e:
            print(f"未知错误 | method:{method} | proxies:{kwargs.get('proxies')} | url:{url} | "
                  f"type:{type(e)} | err:{e.args}")
        retry -= 1
    raise TooManyRetries("请求重试次数过多. url:{url}")


def map_request(method, *args):
    with ThreadPoolExecutor(max_workers=20) as executor:
        fu_list = []
        for kw in args:
            fu_list.append(executor.submit(functools.partial(request, method), **kw))
        wait(fu_list)
        result = []
        for index, f in enumerate(fu_list):
            try:
                result.append(f.result())
            except TooManyRetries:      # 报错就返回最初的传参
                result.append(args[index])
        return result


if __name__ == '__main__':
    pass
