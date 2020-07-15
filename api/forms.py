from flask_wtf.file import FileRequired, FileAllowed
from wtforms import Form, StringField, IntegerField, FileField, BooleanField
from wtforms.validators import DataRequired


"""Captcha 相关"""


class CaptchaTypeForm(Form):
    captcha = FileField("captcha", validators=[
        FileRequired("Please upload your verification code."), FileAllowed(["jpg", "jpeg", "png"])
    ])

    website = StringField("website", validators=[DataRequired("Fill in the type of website.")])
    max_captcha = IntegerField("max_captcha", validators=[DataRequired("Fill in the length of verification code.")])
    char_set = StringField("char_set", validators=[DataRequired("Fill in possible characters of verification code.")])

    username = StringField("username")
    password = StringField("password")
    soft_id = StringField("soft_id")
    code_type = IntegerField("code_type")
    train = BooleanField("train")  # 是否用做训练

    # def validate_code_type(self, field):
    #     CaptchaCode(field.data)     # ValueError


class CaptchaUploadForm(Form):
    captcha = FileField("captcha", validators=[
        FileRequired("Please upload your verification code."), FileAllowed(["jpg", "jpeg", "png"])
    ])

    website = StringField("website", validators=[DataRequired("Fill in the type of website.")])
    max_captcha = IntegerField("max_captcha", validators=[DataRequired("Fill in the length of verification code.")])
    char_set = StringField("char_set", validators=[DataRequired("Fill in possible characters of verification code.")])
    captcha_str = StringField("captcha_str", validators=[DataRequired("Fill in the value of verification code.")])


class CaptchaReportForm(Form):
    captcha_id = IntegerField("captcha_id", validators=[DataRequired("captcha_id Must fill.")])
    md5 = StringField("md5", validators=[DataRequired("md5 Must fill.")])

    username = StringField("username")
    password = StringField("password")
    soft_id = StringField("soft_id")


class CaptchaValidForm(Form):
    filename = StringField("filename", validators=[DataRequired("filename Must fill.")])
    captcha_str = StringField("captcha_str", validators=[DataRequired("Fill in the value of verification code.")])

