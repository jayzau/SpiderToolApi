from enum import Enum


class Status(Enum):

    success = 200       # 正常响应
    busy = 300          # 忙碌，资源不可用
    input_err = 400     # 用户数据提交错误
    system_err = 500    # 系统错误
