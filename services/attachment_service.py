"""
附件管理服务 - 处理单元格文件上传、下载和删除
"""
import os
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from config import DATA_DIR
from utils import rel_path, safe_join


# 附件存储目录
ATTACHMENTS_DIR = os.path.join(DATA_DIR, 'attachments')


def _ensure_attachments_dir():
    """确保附件目录存在"""
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


def _get_attachment_folder(filepath: str, sheet: str, row: int, col: int) -> str:
    """获取单元格附件的存储文件夹路径
    
    路径格式: data/attachments/{file_hash}/{sheet}/{row}_{col}/
    """
    # 使用文件相对路径的哈希作为顶层文件夹
    file_rel = rel_path(filepath)
    file_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, file_rel))[:8]
    
    folder = os.path.join(ATTACHMENTS_DIR, file_hash, sheet, f"{row}_{col}")
    return folder


def save_attachment(
    filepath: str, 
    sheet: str, 
    row: int, 
    col: int, 
    filename: str, 
    file_data: bytes
) -> Tuple[bool, Optional[str], Optional[str]]:
    """保存附件到单元格
    
    Args:
        filepath: Excel 文件的绝对路径
        sheet: 工作表名称
        row: 行索引
        col: 列索引
        filename: 原始文件名
        file_data: 文件二进制数据
        
    Returns:
        (success, attachment_id, error_message)
    """
    try:
        _ensure_attachments_dir()
        
        # 生成唯一的附件ID
        attachment_id = str(uuid.uuid4())[:12]
        
        # 获取存储路径
        folder = _get_attachment_folder(filepath, sheet, row, col)
        os.makedirs(folder, exist_ok=True)
        
        # 清理文件名（移除路径遍历字符）
        safe_filename = os.path.basename(filename)
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '._- ')
        
        # 存储文件: {attachment_id}_{filename}
        stored_filename = f"{attachment_id}_{safe_filename}"
        file_path = os.path.join(folder, stored_filename)
        
        # 写入文件
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # 返回附件信息
        return True, attachment_id, None
        
    except Exception as e:
        return False, None, str(e)


def get_attachment_info(
    filepath: str, 
    sheet: str, 
    row: int, 
    col: int
) -> List[Dict]:
    """获取单元格中的所有附件信息
    
    Returns:
        附件列表，每个附件包含: id, filename, size, mtime
    """
    attachments = []
    
    try:
        folder = _get_attachment_folder(filepath, sheet, row, col)
        
        if not os.path.exists(folder):
            return attachments
        
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            if os.path.isfile(file_path):
                # 解析文件名: {attachment_id}_{original_filename}
                parts = filename.split('_', 1)
                if len(parts) == 2:
                    attachment_id, original_name = parts
                    stat = os.stat(file_path)
                    
                    attachments.append({
                        'id': attachment_id,
                        'filename': original_name,
                        'stored_name': filename,
                        'size': stat.st_size,
                        'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': file_path
                    })
        
        # 按修改时间排序
        attachments.sort(key=lambda x: x['mtime'], reverse=True)
        
    except Exception as e:
        print(f"获取附件信息失败: {e}")
    
    return attachments


def get_attachment_path(
    filepath: str, 
    sheet: str, 
    row: int, 
    col: int, 
    attachment_id: str
) -> Optional[str]:
    """获取附件的完整路径
    
    Args:
        filepath: Excel 文件的绝对路径
        sheet: 工作表名称
        row: 行索引
        col: 列索引
        attachment_id: 附件ID
        
    Returns:
        附件的完整路径，如果不存在则返回 None
    """
    try:
        folder = _get_attachment_folder(filepath, sheet, row, col)
        
        if not os.path.exists(folder):
            return None
        
        # 查找以 attachment_id 开头的文件
        for filename in os.listdir(folder):
            if filename.startswith(attachment_id + '_'):
                return os.path.join(folder, filename)
        
        return None
        
    except Exception as e:
        print(f"获取附件路径失败: {e}")
        return None


def delete_attachment(
    filepath: str, 
    sheet: str, 
    row: int, 
    col: int, 
    attachment_id: str
) -> Tuple[bool, Optional[str]]:
    """删除附件
    
    Returns:
        (success, error_message)
    """
    try:
        file_path = get_attachment_path(filepath, sheet, row, col, attachment_id)
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
            # 如果文件夹为空，删除文件夹
            folder = os.path.dirname(file_path)
            if os.path.exists(folder) and not os.listdir(folder):
                os.rmdir(folder)
                
                # 尝试删除上层文件夹（如果为空）
                parent = os.path.dirname(folder)
                if os.path.exists(parent) and not os.listdir(parent):
                    os.rmdir(parent)
            
            return True, None
        else:
            return False, "附件不存在"
            
    except Exception as e:
        return False, str(e)


def delete_all_attachments(filepath: str, sheet: str, row: int, col: int) -> bool:
    """删除单元格中的所有附件"""
    try:
        folder = _get_attachment_folder(filepath, sheet, row, col)
        
        if os.path.exists(folder):
            shutil.rmtree(folder)
            return True
        
        return True  # 本来就没有附件
        
    except Exception as e:
        print(f"删除所有附件失败: {e}")
        return False


def move_attachments(
    filepath: str, 
    sheet: str, 
    old_row: int, 
    old_col: int,
    new_row: int, 
    new_col: int
) -> bool:
    """移动附件到新的单元格位置（用于拖拽或复制）"""
    try:
        old_folder = _get_attachment_folder(filepath, sheet, old_row, old_col)
        new_folder = _get_attachment_folder(filepath, sheet, new_row, new_col)
        
        if not os.path.exists(old_folder):
            return True  # 没有附件需要移动
        
        os.makedirs(new_folder, exist_ok=True)
        
        # 移动所有附件
        for filename in os.listdir(old_folder):
            old_path = os.path.join(old_folder, filename)
            new_path = os.path.join(new_folder, filename)
            
            if os.path.isfile(old_path):
                shutil.move(old_path, new_path)
        
        # 删除旧文件夹
        os.rmdir(old_folder)
        
        return True
        
    except Exception as e:
        print(f"移动附件失败: {e}")
        return False


def delete_file_attachments(filepath: str) -> bool:
    """删除文件的所有附件（当文件被删除时调用）"""
    try:
        file_rel = rel_path(filepath)
        file_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, file_rel))[:8]
        folder = os.path.join(ATTACHMENTS_DIR, file_hash)
        
        if os.path.exists(folder):
            shutil.rmtree(folder)
        
        return True
        
    except Exception as e:
        print(f"删除文件附件失败: {e}")
        return False


def get_attachment_preview_url(
    filepath: str, 
    sheet: str, 
    row: int, 
    col: int, 
    attachment_id: str
) -> str:
    """生成附件预览/下载的 URL"""
    file_rel = rel_path(filepath)
    return f"/api/attachment/download?file={file_rel}&sheet={sheet}&row={row}&col={col}&id={attachment_id}"


def copy_attachments_to_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """复制附件到快照目录"""
    try:
        file_rel = rel_path(filepath)
        file_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, file_rel))[:8]
        source = os.path.join(ATTACHMENTS_DIR, file_hash)
        
        if not os.path.exists(source):
            return True  # 没有附件
        
        dest = os.path.join(snapshot_dir, 'attachments')
        if os.path.exists(dest):
            shutil.rmtree(dest)
        
        shutil.copytree(source, dest)
        return True
        
    except Exception as e:
        print(f"复制附件到快照失败: {e}")
        return False


def restore_attachments_from_snapshot(filepath: str, snapshot_dir: str) -> bool:
    """从快照恢复附件"""
    try:
        file_rel = rel_path(filepath)
        file_hash = str(uuid.uuid5(uuid.NAMESPACE_URL, file_rel))[:8]
        dest = os.path.join(ATTACHMENTS_DIR, file_hash)
        source = os.path.join(snapshot_dir, 'attachments')
        
        if not os.path.exists(source):
            # 快照中没有附件，删除现有附件
            if os.path.exists(dest):
                shutil.rmtree(dest)
            return True
        
        # 删除现有附件并恢复
        if os.path.exists(dest):
            shutil.rmtree(dest)
        
        shutil.copytree(source, dest)
        return True
        
    except Exception as e:
        print(f"从快照恢复附件失败: {e}")
        return False


def get_storage_size(filepath: Optional[str] = None) -> Dict:
    """获取附件存储统计信息"""
    try:
        if not os.path.exists(ATTACHMENTS_DIR):
            return {'total_size': 0, 'file_count': 0, 'files_by_sheet': {}}
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(ATTACHMENTS_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        # 转换为可读格式
        size_mb = total_size / (1024 * 1024)
        
        return {
            'total_size': total_size,
            'total_size_mb': round(size_mb, 2),
            'file_count': file_count
        }
        
    except Exception as e:
        print(f"获取存储统计失败: {e}")
        return {'total_size': 0, 'total_size_mb': 0, 'file_count': 0}
