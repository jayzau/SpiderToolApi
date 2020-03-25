import datetime


def timedelta_ts(**kwargs):
    """
    获取指定日期的时间戳 以天/小时/分钟为单位 取整
    :param kwargs:
    :return:
    """
    if "minutes" in kwargs:
        value = int(kwargs["minutes"])
        date_str = "%Y-%m-%d %H:%M"
        stf_time = (datetime.datetime.now() + datetime.timedelta(minutes=value)).strftime(date_str)
    elif "hours" in kwargs:
        value = int(kwargs["hours"])
        date_str = "%Y-%m-%d %H"
        stf_time = (datetime.datetime.now() + datetime.timedelta(hours=value)).strftime(date_str)
    elif "days" in kwargs:
        value = int(kwargs["days"])
        date_str = "%Y-%m-%d"
        stf_time = (datetime.datetime.now() + datetime.timedelta(days=value)).strftime(date_str)
    else:
        raise KeyError()
    ts = int(datetime.datetime.strptime(stf_time, date_str).timestamp())
    return ts
