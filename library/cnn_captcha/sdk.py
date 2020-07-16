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


if __name__ == '__main__':
    cnn = CNNCaptcha(
        host="101.200.120.188", port=80,
    )

    def get_pic():
        from random import randint, choice
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO

        WIDTH = 150
        HEIGHT = 50
        CHAR_LENGTH = 4
        FONT_SIZE = 30
        CHARSET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

        img = Image.new('RGB', (WIDTH, HEIGHT), (255, 255, 255))  # 建立一个图片
        draw = ImageDraw.Draw(img)
        for i in range(randint(1, 8)):
            draw.line(xy=[(randint(0, WIDTH), randint(0, HEIGHT)),
                          (randint(0, WIDTH), randint(0, HEIGHT))],
                      fill=(randint(100, 254), randint(100, 254), randint(100, 254)),
                      width=3)
        for i in range(810):
            draw.point(xy=[randint(1, WIDTH - 1), randint(1, HEIGHT - 1)],
                       fill=(randint(0, 254), randint(1, 254), randint(1, 254)),)
        font = ImageFont.truetype(font=FONT, size=FONT_SIZE)
        charset = ""
        for index in range(CHAR_LENGTH):
            char = choice(CHARSET)
            charset += char
            x = int((WIDTH / CHAR_LENGTH * (index + 1) - WIDTH / CHAR_LENGTH / 2))
            if not index:
                x += randint(-20, 0)
            elif index == CHAR_LENGTH:
                x += randint(-10, 10)
            else:
                x += randint(-15, 5)
            y = randint(0, int((HEIGHT - FONT_SIZE) / 2))
            draw.text((x, y), char, font=font,
                      fill=(randint(0, 200), randint(0, 200), randint(0, 200)))
        # img.show()
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        return charset, img_bytes.getvalue()

    print(request("POST", "http://101.200.120.188/api/captcha/train/"))
    # print(request("PUT", "http://101.200.120.188/api/captcha/reload/"))
    # for _ in range(8100):
    #     pic_str, pic_content = get_pic()
    #     pic_str = pic_str.lower()
    #     print(pic_str)
    #     # response = cnn.post_pic(img=pic_content, website="demo", max_captcha=4, char_set="2004")
    #     response = cnn.upload_pic(
    #         img=pic_content, captcha_str=pic_str, website="demo", max_captcha=4, char_set="2004")
    #     print(response)
