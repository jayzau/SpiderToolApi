from enum import Enum, unique


@unique
class ResponseCode(Enum):

    SUCCESS = 20000       # 正常响应
    BUSY = 30000          # 忙碌，资源不可用
    INPUT_ERR = 40000     # 用户数据提交错误
    SYSTEM_ERR = 50000    # 系统错误


if __name__ == '__main__':
    print(ResponseCode(20000))
