from enum import Enum


class Status(Enum):

    success = 200
    busy = 300
    input_err = 400
    system_err = 500
