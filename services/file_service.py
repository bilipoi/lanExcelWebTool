"""
文件操作服务
"""
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

from openpyxl import Workbook

from config import DATA_DIR
from utils import safe_join, rel_path
from services.file_tree import build_tree
from services.meta_service import get_file_meta, load_meta, save_meta
from services.style_service import delete_styles
from models.session import file_sessions


def create_file(parent: str, name: str) -> tuple:
    """创建新文件，返回 (success, result_or_error)"""
    if not name.endswith('.xlsx'):
        name += '.xlsx'
    filepath = safe_join(DATA_DIR, parent, name)
    if filepath is None:
        return False, '非法路径'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 创建空白文件
    wb = Workbook()
    ws = wb.active
    if ws:
        ws.title = 'Sheet1'
    wb.save(filepath)
    wb.close()
    
    return True, {'path': rel_path(filepath), 'tree': build_tree()}


def rename_file(old_rel: str, new_name: str) -> tuple:
    """重命名文件，返回 (success, result_or_error)"""
    if not new_name.endswith('.xlsx'):
        new_name += '.xlsx'
    old_path = safe_join(DATA_DIR, old_rel)
    if old_path is None or not os.path.exists(old_path):
        return False, '文件不存在'
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    os.rename(old_path, new_path)
    
    # 迁移元数据
    meta = load_meta()
    new_rel = rel_path(new_path)
    if old_rel in meta:
        meta[new_rel] = meta.pop(old_rel)
        save_meta(meta)
    
    # 迁移会话
    if old_rel in file_sessions:
        file_sessions[new_rel] = file_sessions.pop(old_rel)
        file_sessions[new_rel].filepath = new_path
        file_sessions[new_rel].rel_path = new_rel
    
    return True, {'tree': build_tree()}


def move_file(src_rel: str, dst_folder: str) -> tuple:
    """移动文件，返回 (success, result_or_error)"""
    src_path = safe_join(DATA_DIR, src_rel)
    dst_dir = safe_join(DATA_DIR, dst_folder)
    if src_path is None or not os.path.exists(src_path):
        return False, '源文件不存在'
    if dst_dir is None or not os.path.isdir(dst_dir):
        return False, '目标文件夹不存在'
    
    dst_path = os.path.join(dst_dir, os.path.basename(src_path))
    shutil.move(src_path, dst_path)
    
    # 迁移元数据
    meta = load_meta()
    new_rel = rel_path(dst_path)
    if src_rel in meta:
        meta[new_rel] = meta.pop(src_rel)
        save_meta(meta)
    
    # 迁移会话
    if src_rel in file_sessions:
        file_sessions[new_rel] = file_sessions.pop(src_rel)
        file_sessions[new_rel].filepath = dst_path
        file_sessions[new_rel].rel_path = new_rel
    
    return True, {'tree': build_tree()}


def delete_file(rel: str) -> tuple:
    """删除文件，返回 (success, result_or_error)"""
    filepath = safe_join(DATA_DIR, rel)
    if filepath is None or not os.path.exists(filepath):
        return False, '文件不存在'
    os.remove(filepath)
    
    # 清理元数据
    meta = load_meta()
    meta.pop(rel, None)
    save_meta(meta)
    
    # 删除样式文件
    delete_styles(filepath)
    
    return True, {'tree': build_tree()}


def set_readonly(rel: str, readonly: bool) -> tuple:
    """设置文件只读权限，返回 (success, result_or_error)"""
    m = get_file_meta(rel)
    m['readonly'] = readonly
    
    # 更新会话状态
    if rel in file_sessions:
        file_sessions[rel].readonly = readonly
    
    meta = load_meta()
    meta[rel] = m
    save_meta(meta)
    
    return True, {'tree': build_tree()}
