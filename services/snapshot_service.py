"""
版本快照服务
"""
import os
import shutil
from datetime import datetime
from typing import Dict, List

from config import SNAP_DIR, MAX_SNAPSHOTS
from utils import rel_path
from .style_service import copy_styles_to_snapshot, restore_styles_from_snapshot


def snapshot_dir_for(filepath: str) -> str:
    """返回该文件对应的快照目录"""
    rel = rel_path(filepath).replace('/', '__')
    d = os.path.join(SNAP_DIR, rel)
    os.makedirs(d, exist_ok=True)
    return d


def create_snapshot(filepath: str) -> str:
    """保存当前文件的快照，返回快照目录名"""
    snap_dir = snapshot_dir_for(filepath)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    snap_subdir = os.path.join(snap_dir, ts)
    os.makedirs(snap_subdir, exist_ok=True)
    
    # Copy Excel file to snapshot subdirectory
    basename = os.path.basename(filepath)
    shutil.copy2(filepath, os.path.join(snap_subdir, basename))
    
    # Backup style file to snapshot subdirectory
    copy_styles_to_snapshot(filepath, snap_subdir)
    
    # Clean up old snapshots (remove oldest directories)
    snaps = sorted([d for d in os.listdir(snap_dir) if os.path.isdir(os.path.join(snap_dir, d))])
    while len(snaps) > MAX_SNAPSHOTS:
        old_snap = snaps.pop(0)
        old_snap_path = os.path.join(snap_dir, old_snap)
        shutil.rmtree(old_snap_path)
    
    return ts


def list_snapshots(filepath: str) -> List[Dict[str, str]]:
    """列出文件的所有快照"""
    snap_dir = snapshot_dir_for(filepath)
    snaps = sorted([d for d in os.listdir(snap_dir) if os.path.isdir(os.path.join(snap_dir, d))], reverse=True)
    result = []
    for s in snaps:
        try:
            dt = datetime.strptime(s, '%Y%m%d_%H%M%S')
            label = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            label = s
        result.append({'name': s, 'label': label})
    return result


def restore_snapshot(filepath: str, snap_name: str) -> bool:
    """恢复到指定快照"""
    snap_dir = snapshot_dir_for(filepath)
    snap_subdir = os.path.join(snap_dir, snap_name)
    if not os.path.exists(snap_subdir) or not os.path.isdir(snap_subdir):
        return False
    
    basename = os.path.basename(filepath)
    snap_file_path = os.path.join(snap_subdir, basename)
    if not os.path.exists(snap_file_path):
        return False
    
    # 恢复前先创建快照
    create_snapshot(filepath)
    
    # Restore Excel file
    shutil.copy2(snap_file_path, filepath)
    
    # Restore style file
    restore_styles_from_snapshot(filepath, snap_subdir)
    
    return True
