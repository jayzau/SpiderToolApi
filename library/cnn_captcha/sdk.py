from requests import request


class CNNCaptcha(object):
    SuperEagle = dict()

    def __init__(self, host="0.0.0.0", port=7118, username='', password='', soft_id=""):
        if all([username, password, soft_id]):
            self.SuperEagle = dict(
                username=username,
                password=password,
                soft_id=soft_id,
            )
        self.base_url = "http://{}:{}/api/captcha/".format(host, port)

    def post_pic(self, img: bytes,
                 website="default", max_captcha=4, char_set="3004",
                 *, eagle=False, code_type=1902, train=False):
        """
        验证码识别
        :param img: 图片流
        :param website: 网站别名
        :param max_captcha: 长度
        :param char_set: 字符集
        :param eagle: 是否使用超级鹰
        :param code_type: 超级鹰code_type
        :param train: 是否用于训练
        :return: 自打码 超级鹰 无法识别
        {'captcha_id': 1, 'captcha_str': '5786', 'err_str': {}, 'error_code': 200,
        'md5': '5fa294fa822dc72f50ef70732505cffd', 'source': 'super_me'}

        {'captcha_id': 2, 'captcha_str': '0084', 'err_str': {}, 'error_code': 200,
        'md5': '0c0ca479933fcfc2e6df4ac495f644a7', 'source': 'super_eagle'}

        {'code': 404, 'error_code': 1000, 'error_str':
        'Not Extended. Please try it again later.', 'request': 'POST /api/captcha/'}
        """
        data = {
            "website": website,
            "max_captcha": max_captcha,
            "char_set": char_set,
        }
        files = {
            "captcha": ("captcha.png", img),
        }
        if eagle and self.SuperEagle:
            data.update(self.SuperEagle)
            data["code_type"] = code_type
        data["train"] = "true" if train else "false"
        url = self.base_url
        resp = request("POST", url=url, data=data, files=files)
        return resp.json()

    def report_error(self, captcha_id: int, md5: str):
        """
        反馈识别错误的验证码
        :param captcha_id: post_pic 返回字段
        :param md5: post_pic 返回字段
        :return:
        {'err_str': {}, 'error_code': 200}
        {'code': 404, 'error_code': 1000,
        'error_str': 'Captcha 1 has been moved.', 'request': 'POST /api/captcha/report/'}
        {'code': 400, 'error_code': 1000,
        'error_str': 'Parameter username, password, soft_id required.', 'request': 'POST /api/captcha/report/'}
        """
        data = {
            "captcha_id": captcha_id,
            "md5": md5,
        }
        if self.SuperEagle:
            data.update(self.SuperEagle)
        url = self.base_url + "report/"
        resp = request("POST", url=url, data=data)
        return resp.json()

    def upload_pic(self, img: bytes, captcha_str: str,
                   website="default", max_captcha=4, char_set="3004"):
        """
        带识别结果上传验证码 用于训练
        :param img:
        :param captcha_str:
        :param website:
        :param max_captcha:
        :param char_set:
        :return:
        """
        data = {
            "website": website,
            "max_captcha": max_captcha,
            "char_set": char_set,
            "captcha_str": captcha_str,
        }
        files = {
            "captcha": ("captcha.png", img),
        }
        url = self.base_url + "upload/"
        resp = request("POST", url=url, data=data, files=files)
        return resp.json()
