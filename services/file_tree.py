"""
文件树服务
"""
import os
from datetime import datetime
from typing import Any, Dict, List

from config import DATA_DIR
from utils import rel_path
from services.meta_service import get_file_meta
from models.session import file_sessions


def build_tree(base: str = DATA_DIR) -> List[Dict[str, Any]]:
    """递归构建文件/文件夹树"""
    result = []
    try:
        entries = sorted(os.scandir(base), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return result
    # 需要隐藏的文件夹名称
    HIDDEN_FOLDERS = {'styles', 'types'}

    for entry in entries:
        # 跳过隐藏文件夹
        if entry.is_dir() and entry.name in HIDDEN_FOLDERS:
            continue

        if entry.is_dir():
            result.append({
                'type': 'folder',
                'name': entry.name,
                'path': rel_path(entry.path),
                'children': build_tree(entry.path)
            })
        elif entry.name.endswith('.xlsx'):
            rp = rel_path(entry.path)
            m = get_file_meta(rp)
            # 检查是否有人在线编辑
            online_count = 0
            if rp in file_sessions:
                online_count = len(file_sessions[rp].online_users)
            result.append({
                'type': 'file',
                'name': entry.name,
                'path': rp,
                'readonly': m.get('readonly', False),
                'online_count': online_count,
                'mtime': datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            })
    return result
