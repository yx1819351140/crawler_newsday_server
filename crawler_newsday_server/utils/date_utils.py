import time
from datetime import datetime
from dateutil import tz, parser
import pytz


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


# 时间戳转时间格式
def timestamp_2_time(timestamp):
    try:
        # 判断时间戳是否是以毫秒为单位
        if len(str(timestamp)) > 10:
            # 如果是毫秒时间戳，将其除以1000转换为秒
            timestamp /= 1000

        # 使用datetime.fromtimestamp将时间戳转换为datetime对象
        dt_object = datetime.fromtimestamp(timestamp)

        # 返回格式化后的时间字符串
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


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


# 美国太平洋时区（PST）时间转时间格式
def pst_2_strftime(time_str):
    # 时区映射字典
    timezone_mapping = {"PST": tz.gettz("America/Los_Angeles")}
    # 解析时间字符串
    parsed_time = parser.parse(time_str, tzinfos=timezone_mapping)
    return parsed_time.strftime("%Y-%m-%d %H:%M:%S")


# 将时间字符串转换为北京时间
def convert_to_beijing_time():
    # 获取当前系统时间
    current_time = datetime.now()

    # 获取当前系统时间的时区信息
    current_timezone = current_time.tzinfo

    # 获取北京时区的时区信息
    beijing_timezone = pytz.timezone('Asia/Shanghai')

    # 判断当前系统时间是否为北京时间
    if current_timezone != beijing_timezone:
        # 如果不是北京时间，将其转换为北京时间
        current_time = datetime.now(beijing_timezone)

    # 返回格式化后的时间字符串
    return current_time.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    # print(time_2_isotime(time.strftime('%Y-%m-%d %H:%M:%S')))
    # print(pst_2_strftime('Fri, 08 Dec 2023 09:37:21 PST'))
    print(timestamp_2_time(1702620354727))
