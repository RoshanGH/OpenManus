import os
import json


def get_subfolders(path):
    """返回指定路径下的所有子文件夹（不包含文件）"""
    subfolders = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            subfolders.append(item)
    return subfolders

def get_json_files(folder_path):
    """获取文件夹下所有 .json 文件"""
    json_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            json_files.append(os.path.join(folder_path, file))
    return json_files


def read_file(file_path, to_json=False, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as f:
        ret = f.read()
    if to_json:
        return json.loads(ret)
    return ret


def write_file(file_path, data, encoding='utf-8'):
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(data)
