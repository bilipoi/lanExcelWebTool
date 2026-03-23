"""
工具函数
"""
import os
import json
import hashlib
from typing import Any, Dict, List, Optional

from config import DATA_DIR


def calc_data_hash(data: Dict[str, List[List[str]]]) -> str:
    """计算当前表格数据的 MD5 指纹，用于判断是否有变更"""
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def get_default_data(rows: int = 50, cols: int = 26) -> List[List[str]]:
    """创建空白表格数据"""
    return [['' for _ in range(cols)] for _ in range(rows)]


def safe_join(base: str, *parts: str) -> Optional[str]:
    """安全拼接路径，防止路径穿越"""
    path = os.path.realpath(os.path.join(base, *parts))
    if not path.startswith(os.path.realpath(base)):
        return None
    return path


def rel_path(abs_path: str) -> str:
    """返回相对 DATA_DIR 的路径，使用正斜杠"""
    return os.path.relpath(abs_path, DATA_DIR).replace('\\', '/')
