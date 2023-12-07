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


# 时间格式转ISODate
def time_2_isotime(time_str):
    try:
        # 解析为 datetime 对象
        parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        # 将时间格式化为 ISO 8601
        iso8601_format = parsed_time.isoformat()
        return iso8601_format
    except:
        return time_str


# 获取两个日期的天数差
def get_days_diff(time_str1, time_str2=time.strftime('%Y-%m-%d')):
    try:
        # 将日期字符串转换为 datetime 对象
        date1 = datetime.strptime(time_str1[:10], "%Y-%m-%d")
        date2 = datetime.strptime(time_str2[:10], "%Y-%m-%d")
        # 计算两个日期之间的差异
        date_difference = date2 - date1
        # 提取差异中的天数部分
        days_difference = date_difference.days
        return days_difference
    except:
        return 0


if __name__ == '__main__':
    print(time_2_isotime(time.strftime('%Y-%m-%d %H:%M:%S')))
