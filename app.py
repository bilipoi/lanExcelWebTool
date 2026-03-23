#!/usr/bin/env python3
"""
局域网多人 Excel 编辑器 - 主入口
"""

from flask import Flask
from flask_socketio import SocketIO

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lan-excel-editor-secret'

# 创建 SocketIO 实例
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# 导入配置
from config import DATA_DIR, SNAP_DIR, BASE_DIR

# 确保目录存在
import os
for d in (DATA_DIR, SNAP_DIR):
    os.makedirs(d, exist_ok=True)

# 导入并注册路由
from handlers.http_handlers import register_http_handlers
from handlers.websocket_handlers import register_websocket_handlers

register_http_handlers(app)
register_websocket_handlers(socketio)

# 启动函数
def run_server(host='0.0.0.0', port=5000, debug=False):
    """启动服务器"""
    from tasks.auto_save import start_auto_save
    
    # 启动自动保存任务
    socketio.start_background_task(start_auto_save, socketio)
    
    print('=' * 50)
    print('  局域网多人 Excel 编辑器（按文件隔离）')
    print(f'  访问地址: http://{host}:{port}')
    print('=' * 50)
    
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server()
