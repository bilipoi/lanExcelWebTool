"""
元数据服务（权限管理）
"""
import json
import os
from typing import Any, Dict

from config import META_FILE


def load_meta() -> Dict[str, Any]:
    """加载元数据文件"""
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_meta(meta: Dict[str, Any]) -> None:
    """保存元数据文件"""
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def get_file_meta(rel_path: str) -> Dict[str, Any]:
    """获取单个文件的元数据，rel_path 为相对 DATA_DIR 的路径"""
    meta = load_meta()
    return meta.get(rel_path, {'readonly': False})


def set_file_meta(rel_path: str, data: Dict[str, Any]) -> None:
    """设置单个文件的元数据"""
    meta = load_meta()
    meta[rel_path] = data
    save_meta(meta)
