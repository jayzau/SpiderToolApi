from flask import request, json
from werkzeug.exceptions import HTTPException


class ApiException(HTTPException):
    code = 500
    msg = 'Whoops! There likes something happening...'
    error_code = 9999

    def __init__(self, code=None, msg=None, error_code=None):
        if code:
            self.code = code
        if msg:
            self.msg = msg
        if error_code:
            self.error_code = error_code
        super(ApiException, self).__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            code=self.code,
            msg=self.msg,
            error_code=self.error_code,
            request=f"{request.method} {self.get_url_no_param()}"
        )
        return json.dumps(body)

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_url = str(request.full_path)
        main_path = full_url.split('?')[0]
        return main_path

