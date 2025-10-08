# -*- coding: UTF-8 -*-
import os
import json
import pickle
import itertools
import hashlib
import os
import pandas as pd


def iter_file_from_dir(folder_path, ext=''):
    """
    从指定文件夹中获取指定后缀名的文件列表
    :param folder_path: 文件夹的绝对路径
    :param file_ext: 指定的文件后缀名，默认为空字符串，表示获取所有类型的文件
    :return: 返回符合条件的文件路径列表
    """
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(ext):
            yield file_path


def walk_file_from_dir(folder_path, ext=''):
    """
    从指定文件夹中遍历指定后缀名的所有文件列表（包含多级子文件夹）
    :param folder_path: 文件夹的绝对路径
    :param file_ext: 指定的文件后缀名，默认为空字符串，表示获取所有类型的文件
    :return: 返回符合条件的文件路径列表
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(ext):
                yield os.path.join(root, file)


def iter_line_from_file(file_path, func=None):
    """
    迭代读取文件的每一行
    :param file_path: 文件的绝对路径
    :param func: 对每行的处理，默认不处理
    :return: 返回文件的每一行内容
    """
    with open(file_path, 'r') as f:
        for line in f:
            if func is not None:
                yield func(line.strip())
            else:
                yield line.strip()


def read_json_file(path, filter_func=None):
    """
    读取json文件
    :param path: json文件的绝对路径
    :param is_json_line: 是否为json_line格式的文件，默认为False
    :param filter_func: 用来筛选每个json对象的lambda函数，默认为None
    :return: 返回json list
    """
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
                if filter_func is not None:
                    json_data = list(filter(filter_func, json_data))
                return json_data
            except Exception as e:
                f.seek(0)
                lines = f.readlines()
                json_list = [json.loads(line.strip(
                )) for line in lines if filter_func is None or filter_func(json.loads(line.strip()))]
                return json_list
    else:
        return None


def write_json_to_file(path: str, data: dict, is_json_line: bool = False) -> None:
    """
    将json写入文件
    :param path: json文件的绝对路径
    :param data: json数据
    :param is_json_line: 是否为json_line格式的文件，默认为False
    :return: None
    """
    valid_path(path)
    with open(path, 'w', encoding='utf-8') as f:
        if is_json_line:
            for line in data:
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        else:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))


def save_as_csv(path: str, data: list, sep: str = '\t'):
    """
    将数据保存为csv文件
    :param path: csv文件的绝对路径
    :param data: 数据
    :return: None
    """
    valid_path(path)
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, encoding='utf-8', sep=sep)


def save_variable_to_bin_file(path, var):
    """
    将Python变量存储为二进制文件

    :param var: 待存储的Python变量
    :param path: 二进制文件存储路径
    :type path: str
    """
    with open(path, 'wb') as f:
        pickle.dump(var, f)


def load_variable_from_bin_file(path):
    """
    从二进制文件中读取Python变量

    :param path: 二进制文件存储路径
    :return: 读取到的Python变量
    """
    with open(path, 'rb') as f:
        var = pickle.load(f)
    return var


def batch_iterator(iterator, batch_size):
    """
    根据batch size yield返回batch数量的对象

    :param iterator: 输入的iterator对象
    :param batch_size: 每个batch的大小
    :return: 返回一个生成器，每次yield返回一个batch的iterator对象
    """
    iterator = iter(iterator)
    while True:
        res = tuple(itertools.islice(iterator, batch_size))
        if not res:
            break
        yield res


def concat_iterators(*iterators):
    """
    拼接多个iterator

    :param iterators: 多个iterator对象
    :type iterators: iterator
    :return: 拼接后的iterator
    :rtype: iterator
    """
    return itertools.chain(*iterators)


def valid_path(path):
    """
    检查路径是否存在，不存在则创建

    :param path: 待检查的路径
    :type path: str
    :return: None
    """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)