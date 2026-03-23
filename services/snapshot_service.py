"""
版本快照服务
"""
import os
import shutil
from datetime import datetime
from typing import Dict, List

from config import SNAP_DIR, MAX_SNAPSHOTS
from utils import rel_path


def snapshot_dir_for(filepath: str) -> str:
    """返回该文件对应的快照目录"""
    rel = rel_path(filepath).replace('/', '__')
    d = os.path.join(SNAP_DIR, rel)
    os.makedirs(d, exist_ok=True)
    return d


def create_snapshot(filepath: str) -> str:
    """保存当前文件的快照，返回快照文件名"""
    snap_dir = snapshot_dir_for(filepath)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    snap_name = f'{ts}.xlsx'
    shutil.copy2(filepath, os.path.join(snap_dir, snap_name))
    snaps = sorted(os.listdir(snap_dir))
    while len(snaps) > MAX_SNAPSHOTS:
        os.remove(os.path.join(snap_dir, snaps.pop(0)))
    return snap_name


def list_snapshots(filepath: str) -> List[Dict[str, str]]:
    """列出文件的所有快照"""
    snap_dir = snapshot_dir_for(filepath)
    snaps = sorted(os.listdir(snap_dir), reverse=True)
    result = []
    for s in snaps:
        ts_str = s.replace('.xlsx', '')
        try:
            dt = datetime.strptime(ts_str, '%Y%m%d_%H%M%S')
            label = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            label = ts_str
        result.append({'name': s, 'label': label})
    return result


def restore_snapshot(filepath: str, snap_name: str) -> bool:
    """恢复到指定快照"""
    snap_dir = snapshot_dir_for(filepath)
    snap_path = os.path.join(snap_dir, snap_name)
    if not os.path.exists(snap_path):
        return False
    # 恢复前先创建快照
    shutil.copy2(filepath, os.path.join(snap_dir, 
        f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'))
    shutil.copy2(snap_path, filepath)
    return True
