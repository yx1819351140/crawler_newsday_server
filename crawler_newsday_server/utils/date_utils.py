import time
from datetime import datetime


# 时间格式转时间戳
def time_2_timestamp(time_str):
    try:
        # 将时间字符串转换为时间对象
        time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        # 获取时间戳
        timestamp = int(time.mktime(time_obj.timetuple()))
        return timestamp
    except:
        return time_str


def time_2_isotime(time_str):
    try:
        # 解析为 datetime 对象
        parsed_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
        # 将时间格式化为 ISO 8601
        iso8601_format = parsed_time.isoformat()
        return iso8601_format
    except:
        return time_str


if __name__ == '__main__':
    pass
