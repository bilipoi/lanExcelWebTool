"""
文件夹操作服务
"""
import os
import shutil

from config import DATA_DIR
from utils import safe_join
from services.file_tree import build_tree


def create_folder(parent: str, name: str) -> tuple:
    """创建文件夹，返回 (success, result_or_error)"""
    path = safe_join(DATA_DIR, parent, name)
    if path is None:
        return False, '非法路径'
    if os.path.exists(path):
        return False, '文件夹已存在'
    os.makedirs(path)
    return True, {'tree': build_tree()}


def rename_folder(old_rel: str, new_name: str) -> tuple:
    """重命名文件夹，返回 (success, result_or_error)"""
    old_path = safe_join(DATA_DIR, old_rel)
    if old_path is None or not os.path.isdir(old_path):
        return False, '文件夹不存在'
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    os.rename(old_path, new_path)
    return True, {'tree': build_tree()}


def delete_folder(rel: str) -> tuple:
    """删除文件夹，返回 (success, result_or_error)"""
    path = safe_join(DATA_DIR, rel)
    if path is None or not os.path.isdir(path):
        return False, '文件夹不存在'
    shutil.rmtree(path)
    return True, {'tree': build_tree()}
