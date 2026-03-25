"""
列类型持久化服务
实时保存到JSON文件，按工作表和列存储类型配置
"""
import json
import os
import shutil
from typing import Dict, Any, Optional

from config import DATA_DIR
from utils import rel_path, safe_join


# 列类型文件存储目录
TYPES_DIR = os.path.join(DATA_DIR, 'types')


def _ensure_types_dir():
    """确保类型目录存在"""
    os.makedirs(TYPES_DIR, exist_ok=True)


def get_type_path(filepath: str) -> Optional[str]:
    """获取Excel文件对应的类型JSON文件路径
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        类型JSON文件的绝对路径，如果路径不安全则返回None
    """
    rel = rel_path(filepath)
    type_filename = rel.replace('/', '__') + '.types.json'
    type_path = safe_join(TYPES_DIR, type_filename)
    return type_path


def save_types(filepath: str, types: Dict[str, Any]) -> bool:
    """保存列类型到JSON文件（实时持久化）
    
    Args:
        filepath: Excel文件的绝对路径
        types: 类型数据字典，格式为 {sheet: {col: type_config}}
        
    Returns:
        是否保存成功
    """
    try:
        type_path = get_type_path(filepath)
        if type_path is None:
            return False
        
        _ensure_types_dir()
        
        with open(type_path, 'w', encoding='utf-8') as f:
            json.dump(types, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存列类型失败: {e}")
        return False


def load_types(filepath: str) -> Dict[str, Any]:
    """从JSON文件加载列类型
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        类型数据字典，如果文件不存在则返回空字典
    """
    try:
        type_path = get_type_path(filepath)
        if type_path is None or not os.path.exists(type_path):
            return {}
        
        with open(type_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载列类型失败: {e}")
        return {}


def delete_types(filepath: str) -> bool:
    """删除类型文件（当Excel文件被删除时调用）
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        是否删除成功（文件不存在也视为成功）
    """
    try:
        type_path = get_type_path(filepath)
        if type_path is None:
            return False
        
        if os.path.exists(type_path):
            os.remove(type_path)
        
        return True
    except Exception as e:
        print(f"删除类型文件失败: {e}")
        return False


def copy_types_to_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """复制类型文件到快照目录
    
    Args:
        filepath: Excel文件的绝对路径
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        是否复制成功（类型文件不存在也视为成功）
    """
    try:
        type_path = get_type_path(filepath)
        if type_path is None:
            return False
        
        if not os.path.exists(type_path):
            # 没有类型文件，视为成功
            return True
        
        # 确保快照目录存在
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # 复制类型文件到快照目录，使用固定名称
        snapshot_type_path = os.path.join(snapshot_dir, 'types.json')
        shutil.copy2(type_path, snapshot_type_path)
        
        return True
    except Exception as e:
        print(f"复制类型到快照失败: {e}")
        return False


def restore_types_from_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """从快照目录恢复类型文件
    
    Args:
        filepath: Excel文件的绝对路径
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        是否恢复成功（快照中没有类型文件也视为成功）
    """
    try:
        snapshot_type_path = os.path.join(snapshot_dir, 'types.json')
        
        if not os.path.exists(snapshot_type_path):
            # 快照中没有类型文件，删除当前类型文件（如果有）
            delete_types(filepath)
            return True
        
        type_path = get_type_path(filepath)
        if type_path is None:
            return False
        
        _ensure_types_dir()
        
        # 恢复类型文件
        shutil.copy2(snapshot_type_path, type_path)
        
        return True
    except Exception as e:
        print(f"从快照恢复类型失败: {e}")
        return False


def get_snapshot_type_path(snapshot_dir: str) -> str:
    """获取快照目录中的类型文件路径
    
    Args:
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        快照类型文件的绝对路径
    """
    return os.path.join(snapshot_dir, 'types.json')
