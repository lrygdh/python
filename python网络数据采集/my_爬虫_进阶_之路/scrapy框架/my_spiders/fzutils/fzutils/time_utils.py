# coding:utf-8

'''
@author = super_fazai
@File    : time_utils.py
@Time    : 2018/7/13 18:02
@connect : superonesfazai@gmail.com
'''

import time

__all__ = [
    'get_shanghai_time',                            # 时区处理，得到上海时间
    'timestamp_to_regulartime',                     # 时间戳转规范的时间字符串
    'string_to_datetime',                           # 将字符串转换成时间
    'datetime_to_timestamp',                        # datetime转timestamp

    'fz_timer',                                     # 一个装饰器或者上下文管理器, 用于计算某函数耗时
    'fz_set_timeout',                               # 可以给任意可能会hang住的函数添加超时功能[这个功能在编写外部API调用, 网络爬虫, 数据库查询的时候特别有用]
]

def get_shanghai_time():
    '''
    时区处理，得到上海时间
    :return: datetime类型
    '''
    import pytz
    import datetime
    import re

    # TODO 时区处理，时间处理到上海时间
    # pytz查询某个国家时区
    # country_timezones_list = pytz.country_timezones('cn')
    # print(country_timezones_list)

    tz = pytz.timezone('Asia/Shanghai')  # 创建时区对象
    now_time = datetime.datetime.now(tz)

    # 处理为精确到秒位，删除时区信息
    now_time = re.compile(r'\..*').sub('', str(now_time))
    # 将字符串类型转换为datetime类型
    now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

    return now_time

def timestamp_to_regulartime(timestamp):
    '''
    将时间戳转换成时间
    '''
    import time
    # 利用localtime()函数将时间戳转化成localtime的格式
    # 利用strftime()函数重新格式化时间

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))

def string_to_datetime(string):
    '''
    将字符串转换成datetime
    :param string:
    :return:
    '''
    import datetime

    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def datetime_to_timestamp(_dateTime):
    '''
    把datetime类型转外时间戳形式
    :param _dateTime:
    :return: int
    '''
    import time

    return int(time.mktime(_dateTime.timetuple()))

class fz_timer(object):
    """
    A timer can time how long does calling take as 上下文管理器 or 装饰器.
    If assign ``print_func`` with ``sys.stdout.write``, ``logger.info`` and so on,
    timer will print the spent time.
        用法: eg:
            import sys

            @fz_timer(print_func=sys.stdout.write)
            def tmp():
                get_shanghai_time()

            tmp()
    """
    def __init__(self, print_func=None):
        '''
        :param print_func: sys.stdout.write | logger.info
        '''
        self.elapsed = None
        self.print_func = print_func

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *_):
        self.elapsed = time.time() - self.start
        if self.print_func:
            self.print_func(self.__str__())

    def __call__(self, fun):
        def wrapper(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)
        return wrapper

    def __str__(self):
        return 'Spent time: {}s'.format(self.elapsed)

class TimeoutError(Exception):
    pass

def fz_set_timeout(seconds, error_message='函数执行超时!'):
    '''
    可以给任意可能会hang住的函数添加超时功能[这个功能在编写外部API调用, 爬虫, 数据库查询的时候特别有用]
        用法: eg:
            from time import sleep

            @fz_set_timeout(seconds=2)
            def tmp():
                sleep(3)

            tmp()
    :param seconds: 设置超时时间
    :param error_message: 显示的错误信息
    :return: None | Exception: 自定义的超时异常TimeoutError
    '''
    import functools
    from threading import Thread

    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            share = [TimeoutError(error_message)]

            def func_with_except():
                try:
                    share[0] = func(*args, **kwargs)
                except Exception as e:
                    share[0] = e

            t = Thread(target=func_with_except)
            t.daemon = True
            try:
                t.start()
                t.join(seconds)
            except Exception as e:
                raise e

            result = share[0]
            if isinstance(result, BaseException):
                raise result

            return result

        return wrapper

    return decorated

