"""
HTTP 路由处理程序
"""
import os
from flask import render_template, request, jsonify, send_file
from typing import Any

from services.file_tree import build_tree
from services.folder_service import create_folder, rename_folder, delete_folder
from services.file_service import create_file, rename_file, move_file, delete_file, set_readonly
from services.snapshot_service import list_snapshots, restore_snapshot
from services.meta_service import get_file_meta
from utils import safe_join
from config import DATA_DIR


def register_http_handlers(app):
    """注册所有 HTTP 路由"""
    
    @app.route('/')
    def index() -> Any:
        return render_template('index.html')
    
    @app.route('/api/tree', methods=['GET'])
    def api_tree():
        return jsonify(build_tree())
    
    # ========== 文件夹操作 ==========
    @app.route('/api/folder/create', methods=['POST'])
    def api_folder_create():
        d = request.get_json() or {}
        parent: str = d.get('parent', '')
        name: str = d.get('name', '').strip()
        if not name:
            return jsonify({'error': '文件夹名不能为空'}), 400
        success, result = create_folder(parent, name)
        if not success:
            return jsonify({'error': result}), 400
        return jsonify(result)
    
    @app.route('/api/folder/rename', methods=['POST'])
    def api_folder_rename():
        d = request.get_json() or {}
        old_rel: str = d.get('path', '')
        new_name: str = d.get('name', '').strip()
        success, result = rename_folder(old_rel, new_name)
        if not success:
            return jsonify({'error': result}), 404
        return jsonify(result)
    
    @app.route('/api/folder/delete', methods=['POST'])
    def api_folder_delete():
        d = request.get_json() or {}
        rel: str = d.get('path', '')
        success, result = delete_folder(rel)
        if not success:
            return jsonify({'error': result}), 404
        return jsonify(result)
    
    # ========== 文件操作 ==========
    @app.route('/api/file/create', methods=['POST'])
    def api_file_create():
        d = request.get_json() or {}
        parent: str = d.get('parent', '')
        name: str = d.get('name', f'新建文件_{datetime.now().strftime("%Y%m%d_%H%M%S")}').strip()
        success, result = create_file(parent, name)
        if not success:
            return jsonify({'error': result}), 400
        return jsonify(result)
    
    @app.route('/api/file/rename', methods=['POST'])
    def api_file_rename():
        d = request.get_json() or {}
        old_rel: str = d.get('path', '')
        new_name: str = d.get('name', '').strip()
        success, result = rename_file(old_rel, new_name)
        if not success:
            return jsonify({'error': result}), 404
        return jsonify(result)
    
    @app.route('/api/file/move', methods=['POST'])
    def api_file_move():
        d = request.get_json() or {}
        src_rel: str = d.get('path', '')
        dst_folder: str = d.get('folder', '')
        success, result = move_file(src_rel, dst_folder)
        if not success:
            return jsonify({'error': result}), 404
        return jsonify(result)
    
    @app.route('/api/file/delete', methods=['POST'])
    def api_file_delete():
        d = request.get_json() or {}
        rel: str = d.get('path', '')
        success, result = delete_file(rel)
        if not success:
            return jsonify({'error': result}), 404
        return jsonify(result)
    
    @app.route('/api/file/download')
    def api_file_download():
        rel: str = request.args.get('path', '')
        filepath = safe_join(DATA_DIR, rel)
        if filepath is None or not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
        return send_file(filepath, as_attachment=True)
    
    @app.route('/api/file/readonly', methods=['POST'])
    def api_file_readonly():
        d = request.get_json() or {}
        rel: str = d.get('path', '')
        readonly: bool = bool(d.get('readonly', False))
        success, result = set_readonly(rel, readonly)
        return jsonify(result)
    
    # ========== 版本快照 ==========
    @app.route('/api/snapshots', methods=['GET'])
    def api_list_snapshots():
        rel: str = request.args.get('path', '')
        filepath = safe_join(DATA_DIR, rel)
        if filepath is None or not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
        return jsonify(list_snapshots(filepath))
    
    @app.route('/api/snapshots/restore', methods=['POST'])
    def api_restore_snapshot():
        d = request.get_json() or {}
        rel: str = d.get('path', '')
        snap_name: str = d.get('snapshot', '')
        filepath = safe_join(DATA_DIR, rel)
        if filepath is None or not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
        if not restore_snapshot(filepath, snap_name):
            return jsonify({'error': '快照不存在'}), 404
        return jsonify({'ok': True})


# 导入 datetime 用于创建文件名
from datetime import datetime
