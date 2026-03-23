"""
单元格样式持久化服务 - 混合模式
实时保存到JSON文件，快照时复制样式文件
"""
import json
import os
import shutil
from typing import Dict, Any, Optional

from config import DATA_DIR
from utils import rel_path, safe_join


# 样式文件存储目录
STYLES_DIR = os.path.join(DATA_DIR, 'styles')


def _ensure_styles_dir():
    """确保样式目录存在"""
    os.makedirs(STYLES_DIR, exist_ok=True)


def get_style_path(filepath: str) -> Optional[str]:
    """获取Excel文件对应的样式JSON文件路径
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        样式JSON文件的绝对路径，如果路径不安全则返回None
    """
    rel = rel_path(filepath)
    style_filename = rel.replace('/', '__') + '.styles.json'
    style_path = safe_join(STYLES_DIR, style_filename)
    return style_path


def save_styles(filepath: str, styles: Dict[str, Any]) -> bool:
    """保存样式到JSON文件（实时持久化）
    
    Args:
        filepath: Excel文件的绝对路径
        styles: 样式数据字典，格式为 {sheet: {row: {col: style_dict}}}
        
    Returns:
        是否保存成功
    """
    try:
        style_path = get_style_path(filepath)
        if style_path is None:
            return False
        
        _ensure_styles_dir()
        
        with open(style_path, 'w', encoding='utf-8') as f:
            json.dump(styles, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存样式失败: {e}")
        return False


def load_styles(filepath: str) -> Dict[str, Any]:
    """从JSON文件加载样式
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        样式数据字典，如果文件不存在则返回空字典
    """
    try:
        style_path = get_style_path(filepath)
        if style_path is None or not os.path.exists(style_path):
            return {}
        
        with open(style_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载样式失败: {e}")
        return {}


def delete_styles(filepath: str) -> bool:
    """删除样式文件（当Excel文件被删除时调用）
    
    Args:
        filepath: Excel文件的绝对路径
        
    Returns:
        是否删除成功（文件不存在也视为成功）
    """
    try:
        style_path = get_style_path(filepath)
        if style_path is None:
            return False
        
        if os.path.exists(style_path):
            os.remove(style_path)
        
        return True
    except Exception as e:
        print(f"删除样式文件失败: {e}")
        return False


def copy_styles_to_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """复制样式文件到快照目录
    
    Args:
        filepath: Excel文件的绝对路径
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        是否复制成功（样式文件不存在也视为成功）
    """
    try:
        style_path = get_style_path(filepath)
        if style_path is None:
            return False
        
        if not os.path.exists(style_path):
            # 没有样式文件，视为成功
            return True
        
        # 确保快照目录存在
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # 复制样式文件到快照目录，使用固定名称
        snapshot_style_path = os.path.join(snapshot_dir, 'styles.json')
        shutil.copy2(style_path, snapshot_style_path)
        
        return True
    except Exception as e:
        print(f"复制样式到快照失败: {e}")
        return False


def restore_styles_from_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """从快照目录恢复样式文件
    
    Args:
        filepath: Excel文件的绝对路径
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        是否恢复成功（快照中没有样式文件也视为成功）
    """
    try:
        snapshot_style_path = os.path.join(snapshot_dir, 'styles.json')
        
        if not os.path.exists(snapshot_style_path):
            # 快照中没有样式文件，删除当前样式文件（如果有）
            delete_styles(filepath)
            return True
        
        style_path = get_style_path(filepath)
        if style_path is None:
            return False
        
        _ensure_styles_dir()
        
        # 恢复样式文件
        shutil.copy2(snapshot_style_path, style_path)
        
        return True
    except Exception as e:
        print(f"从快照恢复样式失败: {e}")
        return False


def get_snapshot_style_path(snapshot_dir: str) -> str:
    """获取快照目录中的样式文件路径
    
    Args:
        snapshot_dir: 快照目录的绝对路径
        
    Returns:
        快照样式文件的绝对路径
    """
    return os.path.join(snapshot_dir, 'styles.json')
