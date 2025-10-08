from hashlib import md5
from datetime import datetime
import os
import pprint
from json.encoder import JSONEncoder
import json


def generate_four_digit_code(string):
    # 使用MD5算法计算哈希值
    md5_hash = md5(string.encode()).hexdigest()
    # 取MD5哈希值的前四位作为四位编码
    four_digit_code = md5_hash[:4]

    return four_digit_code


def generate_md5_hash(string):
    # 使用MD5算法计算哈希值
    md5_hash = md5(string.encode()).hexdigest()
    return md5_hash


def get_date_suffix():
    return datetime.now().strftime('%m%d')


def get_env_vars(var_name):
    # 获取环境变量的值
    value = os.environ.get(var_name)
    # 检查环境变量是否存在
    if var_name in os.environ:
        # 存在环境变量
        value = os.environ[var_name]
    else:
        # 不存在环境变量
        value = None
    return value


def pprint_dict(dict):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(dict)


def get_enum_from_val(Enum, val):
    # 获取枚举类的所有成员
    members = Enum.__members__
    # 遍历枚举类的所有成员
    for member in members:
        # 获取枚举类成员的值
        member_val = members[member].value
        # 检查枚举类成员的值是否与输入值相等
        if member_val == val:
            # 返回枚举类成员
            return members[member]
    # 如果没有找到匹配的枚举类成员，则返回None
    return None


class DictObjEncoder(JSONEncoder):
    def default(self, obj):
        # if instance has method to_dict, call it
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)


def dict_obj_to_json(obj):
    return json.dumps(obj, cls=DictObjEncoder)
