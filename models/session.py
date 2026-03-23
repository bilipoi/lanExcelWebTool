"""
文件会话模型
"""
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from config import DATA_DIR, SNAP_DIR, USER_COLORS, MAX_SNAPSHOTS
from utils import rel_path, calc_data_hash, get_default_data


class FileSession:
    """单个文件的会话状态"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath                    # 文件绝对路径
        self.rel_path = rel_path(filepath)          # 相对路径（作为 room name）
        self.spreadsheet_data: Dict[str, List[List[str]]] = {}
        self.last_saved_hash: str = ''              # 上次保存的数据指纹
        # 用户信息：{sid: {'username': str, 'color': str, 'selection': {sheet, row, col}}}
        self.online_users: Dict[str, Dict[str, Any]] = {}
        self.readonly: bool = False                 # 只读状态
        self._color_index = 0                       # 颜色分配索引
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """从磁盘加载 Excel 数据"""
        if not os.path.exists(self.filepath):
            # 文件不存在，创建空白
            self.spreadsheet_data = {'Sheet1': get_default_data()}
            self.last_saved_hash = calc_data_hash(self.spreadsheet_data)
            return
        
        wb = load_workbook(self.filepath)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            if not isinstance(ws, Worksheet):
                continue
            rows: List[List[str]] = []
            max_row = max(ws.max_row or 1, 50)
            max_col = max(ws.max_column or 1, 26)
            for r in range(1, max_row + 1):
                row: List[str] = []
                for c in range(1, max_col + 1):
                    val = ws.cell(row=r, column=c).value
                    row.append(str(val) if val is not None else '')
                rows.append(row)
            self.spreadsheet_data[sheet_name] = rows
        wb.close()
        self.last_saved_hash = calc_data_hash(self.spreadsheet_data)
        
        # 加载只读权限
        from services.meta_service import get_file_meta
        m = get_file_meta(self.rel_path)
        self.readonly = m.get('readonly', False)
    
    def save(self) -> bool:
        """保存到磁盘，如有变更则返回 True"""
        current_hash = calc_data_hash(self.spreadsheet_data)
        if current_hash == self.last_saved_hash:
            return False  # 无变更
        
        wb = Workbook()
        default_sheet = wb.active
        if default_sheet is not None:
            wb.remove(default_sheet)
        for sheet_name, data in self.spreadsheet_data.items():
            ws = wb.create_sheet(title=sheet_name)
            for r_idx, row in enumerate(data, 1):
                for c_idx, val in enumerate(row, 1):
                    if val and val.strip():
                        try:
                            ws.cell(row=r_idx, column=c_idx, value=float(val))
                        except (ValueError, TypeError):
                            ws.cell(row=r_idx, column=c_idx, value=val)
        wb.save(self.filepath)
        wb.close()
        
        self.last_saved_hash = current_hash
        return True
    
    def _get_next_color(self) -> str:
        """获取下一个可用颜色"""
        color = USER_COLORS[self._color_index % len(USER_COLORS)]
        self._color_index += 1
        return color
    
    def add_user(self, sid: str, username: str) -> str:
        """添加用户，返回分配的颜色"""
        color = self._get_next_color()
        self.online_users[sid] = {
            'username': username,
            'color': color,
            'selection': None  # {sheet, row, col}
        }
        return color
    
    def remove_user(self, sid: str) -> Optional[Dict[str, Any]]:
        """移除用户"""
        user_info = self.online_users.pop(sid, None)
        return user_info
    
    def update_selection(self, sid: str, sheet: str, row: int, col: int) -> Optional[Dict[str, Any]]:
        """更新用户选中的单元格"""
        if sid not in self.online_users:
            return None
        self.online_users[sid]['selection'] = {'sheet': sheet, 'row': row, 'col': col}
        return self.online_users[sid]
    
    def clear_selection(self, sid: str) -> Optional[Dict[str, Any]]:
        """清除用户选中"""
        if sid not in self.online_users:
            return None
        self.online_users[sid]['selection'] = None
        return self.online_users[sid]
    
    def get_user_list(self) -> List[Dict[str, Any]]:
        """获取用户列表（包含颜色和选中信息）"""
        return [
            {
                'username': info['username'],
                'color': info['color'],
                'selection': info['selection']
            }
            for info in self.online_users.values()
        ]
    
    def get_other_users_selections(self, exclude_sid: str) -> List[Dict[str, Any]]:
        """获取其他用户的选中状态"""
        result = []
        for sid, info in self.online_users.items():
            if sid != exclude_sid and info['selection']:
                result.append({
                    'username': info['username'],
                    'color': info['color'],
                    'selection': info['selection']
                })
        return result
    
    def is_empty(self) -> bool:
        return len(self.online_users) == 0


# 全局会话管理：{rel_path: FileSession}
file_sessions: Dict[str, FileSession] = {}

# 记录每个 sid 当前所在的文件 room
user_current_file: Dict[str, str] = {}


def get_or_create_session(filepath: str) -> FileSession:
    """获取或创建文件会话"""
    rel = rel_path(filepath)
    if rel not in file_sessions:
        file_sessions[rel] = FileSession(filepath)
    return file_sessions[rel]


def cleanup_empty_sessions() -> None:
    """清理无人在线的会话，释放内存"""
    empty = [rel for rel, sess in file_sessions.items() if sess.is_empty()]
    for rel in empty:
        del file_sessions[rel]
