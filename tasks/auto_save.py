"""
自动保存任务
"""
import time
from models.session import file_sessions
from services.snapshot_service import create_snapshot


def start_auto_save(socketio):
    """启动自动保存循环"""
    while True:
        socketio.sleep(30)  # 每 30 秒检查一次
        
        for rel, sess in list(file_sessions.items()):
            if sess.readonly or sess.is_empty():
                continue
            try:
                changed = sess.save()
                if changed:
                    create_snapshot(sess.filepath)
                    print(f'[自动保存] {rel}')
                else:
                    print(f'[自动保存跳过] {rel} - 内容无变更')
            except Exception as e:
                print(f'[自动保存失败] {rel}: {e}')
