"""
WebSocket 事件处理程序
"""
import os
from flask import request
from flask_socketio import emit, join_room, leave_room

from config import DATA_DIR
from utils import safe_join, rel_path
from models.session import get_or_create_session, file_sessions, user_current_file, cleanup_empty_sessions
from services.snapshot_service import create_snapshot
from services.meta_service import get_file_meta
from services.style_service import save_styles, delete_styles


def register_websocket_handlers(socketio):
    """注册所有 WebSocket 事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        sid = request.sid
        print(f'[连接] {sid}')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        # 从当前文件离开
        if sid in user_current_file:
            rel = user_current_file[sid]
            if rel in file_sessions:
                sess = file_sessions[rel]
                user_info = sess.remove_user(sid)
                # 广播用户离开和选中清除
                emit('user_left', {
                    'username': user_info['username'] if user_info else '未知用户',
                    'users': sess.get_user_list()
                }, room=rel, broadcast=True)
                # 广播清除该用户的选中指示器
                emit('selection_cleared', {'sid': sid}, room=rel, broadcast=True)
                print(f'[离开文件] {user_info["username"] if user_info else "未知"} 离开 {rel}')
                # 如果文件空了，清理会话
                if sess.is_empty():
                    del file_sessions[rel]
            del user_current_file[sid]
        print(f'[断开] {sid}')
    
    @socketio.on('join_file')
    def handle_join_file(data):
        """用户加入某个文件的编辑"""
        sid = request.sid
        rel = data.get('path', '')
        username = data.get('username', f'用户_{sid[:6]}')
        
        filepath = safe_join(DATA_DIR, rel)
        if filepath is None or not os.path.exists(filepath):
            emit('error', {'message': '文件不存在'})
            return
        
        # 如果已经在其他文件，先离开
        if sid in user_current_file and user_current_file[sid] != rel:
            old_rel = user_current_file[sid]
            if old_rel in file_sessions:
                old_sess = file_sessions[old_rel]
                old_user_info = old_sess.remove_user(sid)
                leave_room(old_rel)
                emit('user_left', {
                    'username': old_user_info['username'] if old_user_info else '未知用户',
                    'users': old_sess.get_user_list()
                }, room=old_rel, broadcast=True)
                # 广播清除选中
                emit('selection_cleared', {'sid': sid}, room=old_rel, broadcast=True)
        
        # 加入新文件
        sess = get_or_create_session(filepath)
        user_color = sess.add_user(sid, username)
        user_current_file[sid] = rel
        join_room(rel)
        
        # 发送文件数据给该用户（包含其他用户的选中状态）
        emit('file_opened', {
            'path': rel,
            'filename': os.path.basename(filepath),
            'sheets': sess.spreadsheet_data,
            'cell_styles': sess.cell_styles,
            'readonly': sess.readonly,
            'users': sess.get_user_list(),
            'my_color': user_color,
            'other_selections': sess.get_other_users_selections(sid)
        })
        
        # 通知该文件的其他用户
        emit('user_joined', {
            'username': username,
            'color': user_color,
            'users': sess.get_user_list()
        }, room=rel, broadcast=True, include_self=False)
        
        print(f'[加入文件] {username}({user_color}) 加入 {rel}')
    
    @socketio.on('leave_file')
    def handle_leave_file(data):
        """用户主动离开当前文件"""
        sid = request.sid
        if sid not in user_current_file:
            return
        
        rel = user_current_file[sid]
        if rel in file_sessions:
            sess = file_sessions[rel]
            user_info = sess.remove_user(sid)
            leave_room(rel)
            emit('user_left', {
                'username': user_info['username'] if user_info else '未知用户',
                'users': sess.get_user_list()
            }, room=rel, broadcast=True)
            # 广播清除选中
            emit('selection_cleared', {'sid': sid}, room=rel, broadcast=True)
            print(f'[离开文件] {user_info["username"] if user_info else "未知"} 离开 {rel}')
            if sess.is_empty():
                del file_sessions[rel]
        
        del user_current_file[sid]
        emit('left_file', {'path': rel})
    
    @socketio.on('cell_select')
    def handle_cell_select(data):
        """处理单元格选中（协作指示器）"""
        sid = request.sid
        
        if sid not in user_current_file:
            return
        
        rel = user_current_file[sid]
        if rel not in file_sessions:
            return
        
        sess = file_sessions[rel]
        sheet = data.get('sheet', 'Sheet1')
        row = int(data.get('row', -1))
        col = int(data.get('col', -1))
        
        # 更新用户的选中状态
        user_info = sess.update_selection(sid, sheet, row, col)
        if user_info:
            # 广播给其他用户
            emit('cell_selected', {
                'sid': sid,
                'username': user_info['username'],
                'color': user_info['color'],
                'sheet': sheet,
                'row': row,
                'col': col
            }, room=rel, broadcast=True, include_self=False)
    
    @socketio.on('cell_deselect')
    def handle_cell_deselect():
        """处理单元格取消选中"""
        sid = request.sid
        
        if sid not in user_current_file:
            return
        
        rel = user_current_file[sid]
        if rel not in file_sessions:
            return
        
        sess = file_sessions[rel]
        sess.clear_selection(sid)
        
        # 广播给其他用户
        emit('selection_cleared', {'sid': sid}, room=rel, broadcast=True)
    
    @socketio.on('cell_edit')
    def handle_cell_edit(data):
        """处理单元格编辑"""
        sid = request.sid
        
        # 检查用户是否在编辑文件
        if sid not in user_current_file:
            return
        
        rel = user_current_file[sid]
        if rel not in file_sessions:
            return
        
        sess = file_sessions[rel]
        
        # 只读检查
        if sess.readonly:
            emit('error', {'message': '文件为只读，无法编辑'})
            return
        
        sheet = data.get('sheet', 'Sheet1')
        row = int(data.get('row', 0))
        col = int(data.get('col', 0))
        value = str(data.get('value', ''))
        
        user_info = sess.online_users.get(sid)
        username = user_info['username'] if user_info else '未知'
        
        # 更新数据
        if sheet in sess.spreadsheet_data:
            while row >= len(sess.spreadsheet_data[sheet]):
                cols_count = len(sess.spreadsheet_data[sheet][0]) if sess.spreadsheet_data[sheet] else 26
                sess.spreadsheet_data[sheet].append(['' for _ in range(cols_count)])
            while col >= len(sess.spreadsheet_data[sheet][row]):
                sess.spreadsheet_data[sheet][row].append('')
            sess.spreadsheet_data[sheet][row][col] = value
        
        # 只广播给同一文件的 Room
        emit('cell_updated', {
            'sheet': sheet, 'row': row, 'col': col,
            'value': value, 'username': username
        }, room=rel, broadcast=True, include_self=False)
    
    @socketio.on('save_file')
    def handle_save_file():
        """手动保存"""
        sid = request.sid
        if sid not in user_current_file:
            emit('save_result', {'ok': False, 'error': '没有打开的文件'})
            return
        
        rel = user_current_file[sid]
        if rel not in file_sessions:
            emit('save_result', {'ok': False, 'error': '会话不存在'})
            return
        
        sess = file_sessions[rel]
        
        if sess.readonly:
            emit('save_result', {'ok': False, 'error': '文件为只读'})
            return
        
        changed = sess.save()
        if changed:
            create_snapshot(sess.filepath)
            emit('save_result', {'ok': True, 'saved': True, 'message': '已保存'})
            # 通知同一文件的其他用户
            emit('file_saved', {'by': sess.online_users.get(sid, {}).get('username', '未知')}, room=rel, broadcast=True, include_self=False)
        else:
            emit('save_result', {'ok': True, 'saved': False, 'message': '内容无变更'})
    
    @socketio.on('cell_style_change')
    def handle_cell_style_change(data):
        """处理单元格样式变更"""
        sid = request.sid
        
        # 检查用户是否在编辑文件
        if sid not in user_current_file:
            return
        
        rel = user_current_file[sid]
        if rel not in file_sessions:
            return
        
        sess = file_sessions[rel]
        
        # 只读检查
        if sess.readonly:
            emit('error', {'message': '文件为只读，无法修改样式'})
            return
        
        sheet = data.get('sheet', 'Sheet1')
        row = int(data.get('row', 0))
        col = int(data.get('col', 0))
        style_type = data.get('style_type', '')
        value = data.get('value')
        
        user_info = sess.online_users.get(sid)
        username = user_info['username'] if user_info else '未知'
        
        # 更新样式数据
        if sheet not in sess.cell_styles:
            sess.cell_styles[sheet] = {}
        if str(row) not in sess.cell_styles[sheet]:
            sess.cell_styles[sheet][str(row)] = {}
        if str(col) not in sess.cell_styles[sheet][str(row)]:
            sess.cell_styles[sheet][str(row)][str(col)] = {}
        
        sess.cell_styles[sheet][str(row)][str(col)][style_type] = value
        
        # 保存到磁盘
        save_styles(sess.filepath, sess.cell_styles)
        
        # 广播给同一文件的其他用户
        emit('cell_style_updated', {
            'sheet': sheet,
            'row': row,
            'col': col,
            'style_type': style_type,
            'value': value,
            'username': username
        }, room=rel, broadcast=True, include_self=False)
