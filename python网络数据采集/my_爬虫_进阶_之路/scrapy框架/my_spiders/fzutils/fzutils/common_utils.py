# coding:utf-8

'''
@author = super_fazai
@File    : common_utils.py
@Time    : 2018/7/13 18:19
@connect : superonesfazai@gmail.com
'''

from pprint import pprint

__all__ = [
    'json_2_dict',                                              # json转dict
    '_green',                                                   # 将字体变成绿色
    'delete_list_null_str',                                     # 删除list中的空str
    'list_duplicate_remove',                                    # list去重
    'len_pro',                                                  # 获取具有 __len__, len, fileno, tell 等属性的对象的长度, 比如: list, tuple, dict, file and so on

    # json_str转dict时报错处理方案
    'deal_with_JSONDecodeError_about_value_invalid_escape',     # 错误如: ValueError: Invalid \escape: line 1 column 35442 (char 35441)

    '_print',                                                   # fz的输出方式(常规print or logger打印)

    # 随机
    'get_random_int_number',                                    # 得到一个随机的int数字

    'wash_sensitive_info',                                      # 清洗敏感字符

    # img
    'save_base64_img_2_local',                                  # 存储类似data:image/jpg;base64,xxxxxx的图片到本地
]

def json_2_dict(json_str, logger=None, encoding=None):
    '''
    json字符串转dict
    :param json_str:
    :param logger:
    :param encoding: 解码格式
    :return:
    '''
    from json import (
        loads,
        JSONDecodeError,)
    from demjson import decode

    _ = {}
    try:
        _ = loads(json_str)
    except JSONDecodeError:
        # 上方解码失败! 采用demjson二次解码
        try:
            _ = decode(json_str, encoding=encoding)
        except Exception as e:
            _print(msg='遇到json解码错误!', logger=logger, log_level=2, exception=e)

    return _

def _green(string):
    '''
    将字体转变为绿色
    :param string:
    :return:
    '''
    return '\033[32m{}\033[0m'.format(string)

def delete_list_null_str(_list):
    '''
    删除list中的所有空str
    :param _list:
    :return:
    '''
    while '' in _list:
        _list.remove('')

    return _list

def list_duplicate_remove(_list:list):
    '''
    list去重
    :param _list:
    :return:
    '''
    b = []
    [b.append(i) for i in _list if not i in b]

    return b

def deal_with_JSONDecodeError_about_value_invalid_escape(json_str):
    '''
    ValueError: Invalid \escape: line 1 column 35442 (char 35441)
    问题在于编码中是\xa0之类的，当遇到有些 不用转义的\http之类的，则会出现以上错误。
    :param json_str:
    :return: 正常的str类型的json字符串
    '''
    import re

    return re.compile(r'\\(?![/u"])').sub(r"\\\\", json_str)

def _print(**kwargs):
    '''
    fz的输出方式(常规print or logger打印)
        可传特殊形式:
            eg: _print(exception=e, logger=logger)  # logger可以为None
    :param kwargs:
    :return: None
    '''
    msg = kwargs.get('msg', None)
    logger = kwargs.get('logger', None)
    log_level = kwargs.get('log_level', 1)     # 日志等级(默认'info')
    exception = kwargs.get('exception', None)

    if not logger:
        if not exception:
            print(msg)
        else:
            if not msg:
                print(msg, exception)
            else:
                print(exception)
    else:
        if not msg:
            if isinstance(msg, str):
                if isinstance(log_level, int):
                    if log_level == 1:
                        logger.info(msg)
                    elif log_level == 2:
                        logger.error(msg)
                    else:
                        raise ValueError('log_level没有定义该打印等级!')
                else:
                    raise TypeError('log_level类型错误!')
            else:
                raise TypeError('log模式打印时, msg必须是str!')

        if not exception:
            if isinstance(exception, Exception):
                logger.exception(exception)
            else:
                raise TypeError('exception必须是Exception类型!')

    return True

def get_random_int_number(start_num=0, end_num=1000):
    '''
    得到一个随机的int数字
    :param start_num:
    :param end_num:
    :return:
    '''
    from random import randint

    return randint(start_num, end_num)

def wash_sensitive_info(data, replace_str_list=None, add_sensitive_str_list=None):
    '''
    清洗敏感字符
    :param data: 待清洗的str
    :param replace_str_list: 需要被替换的list(会被替换为元组中的第2个元素) eg: [('123', '456'), ...]
    :param add_sensitive_str_list: 增加的过滤敏感词汇(会被替换为'') eg: ['123', '456', ...]
    :return: a str
    '''
    import re

    if replace_str_list is not None:            # replace
        if isinstance(replace_str_list, list):
            for item in replace_str_list:
                try:
                    before_str = r'{0}'.format(item[0])
                    end_str = r'{0}'.format(item[1])
                except IndexError:
                    raise IndexError('获取replace_str_list的子元素时索引异常, 请检查!')
                data = re.compile(before_str).sub(end_str, data)
        else:
            raise TypeError('replace_str只支持list类型! eg: [("123", "456"), ...]')

    if add_sensitive_str_list is not None:      # add sensitive_str to ''
        if isinstance(add_sensitive_str_list, list):
            for item in add_sensitive_str_list:
                data = re.compile(r'{0}'.format(item)).sub('', data)
        else:
            raise TypeError('add_sensitive_str_list只支持list类型! eg: ["123", "456", ...]')

    # TODO 不过滤\u200a, \u200d类似字符(显示后有实际意义)
    tmp_str = r'''
    淘宝|taobao|TAOBAO|天猫|tmall|TMALL|
    京东|JD|jd|红书爸爸|共产党|邪教|艹|折800|
    杀人|胡锦涛|江泽民|习近平|小红薯|毛泽东|
    拉粑粑
    '''.replace(' ', '').replace('\n', '')
    data = re.compile(tmp_str).sub('', data)

    data = re.compile(r'\xa0').sub(' ', data)  # '\xa0' 是不间断空白符 &nbsp;

    return data

def save_base64_img_2_local(save_path, base64_img_str):
    '''
    存储类似data:image/jpg;base64,xxxxxx的图片到本地
    :param save_path: 存储的路径
    :param base64_img_str:
    :return:
    '''
    import base64

    try:
        ## 将base64转换位图片存储
        # print(base64_img_str)
        base64_img_str = base64_img_str[base64_img_str.find(",") + 1:]  # 得到data:image/jpg;base64,后面的图片的base64格式的字符串
        # print(base64_img_str)
        with open(save_path, 'wb') as f:
            base64_img_str = base64.b64decode(base64_img_str)
            f.write(base64_img_str)

        return True
    except Exception as e:
        print(e)
        return False

def len_pro(obj):
    '''
    获取具有 __len__, len, fileno, tell 等属性的对象的长度, 比如: list, tuple, dict, file and so on
    :param obj:
    :return: 长度 int
    '''
    import os
    import io

    total_length = None
    current_position = 0

    if hasattr(obj, '__len__'):
        total_length = len(obj)

    elif hasattr(obj, 'len'):
        total_length = obj.len

    elif hasattr(obj, 'fileno'):
        try:
            fileno = obj.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            total_length = os.fstat(fileno).st_size

    if hasattr(obj, 'tell'):
        try:
            current_position = obj.tell()
        except (OSError, IOError):
            # This can happen in some weird situations, such as when the file
            # is actually a special file descriptor like stdin. In this
            # instance, we don't know what the length is, so set it to zero and
            # let requests chunk it instead.
            if total_length is not None:
                current_position = total_length
        else:
            if hasattr(obj, 'seek') and total_length is None:
                # StringIO and BytesIO have seek but no useable fileno
                try:
                    # seek to end of file
                    obj.seek(0, 2)
                    total_length = obj.tell()

                    # seek back to current position to support
                    # partially read file-like objects
                    obj.seek(current_position or 0)
                except (OSError, IOError):
                    total_length = 0

    if total_length is None:
        total_length = 0

    return max(0, total_length - current_position)

