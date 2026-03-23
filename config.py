"""
配置文件
"""
import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, 'data')        # 存放 xlsx 文件（含子文件夹）
SNAP_DIR = os.path.join(BASE_DIR, 'snapshots')   # 版本快照
META_FILE = os.path.join(BASE_DIR, 'meta.json')  # 文件元数据（权限等）

# 常量
MAX_SNAPSHOTS = 20  # 每个文件最多保留快照数

# 用户颜色池（用于协作指示器）
USER_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#6C5CE7',
    '#A29BFE', '#FD79A8', '#FDCB6E', '#00B894',
    '#E17055', '#74B9FF', '#00CEC9', '#FAB1A0'
]
