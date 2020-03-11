from wtforms import Form, StringField
from wtforms.validators import DataRequired, ValidationError

from library.cookie_pool.settings import GENERATOR_MAP


class AddAccountForm(Form):
    website = StringField("website", validators=[DataRequired()])
    account = StringField("account", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])

    def validate_website(self, field):
        if field.data not in GENERATOR_MAP.keys():
            raise ValidationError('website type error.')


class DelAccountForm(Form):
    website = StringField("website", validators=[DataRequired()])
    account = StringField("account", validators=[DataRequired()])

    def validate_website(self, field):
        if field.data not in GENERATOR_MAP.keys():
            raise ValidationError('website type error.')
