#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包工具 - 创建干净的离线安装包
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def create_offline_package():
    """创建离线安装包"""
    
    print("=" * 60)
    print("  局域网 Excel 编辑器 - 离线打包工具")
    print("=" * 60)
    print()
    
    # 检查当前目录
    if not os.path.exists("app.py"):
        print("[错误] 请在项目根目录运行此脚本")
        return False
    
    # 定义排除项
    exclude_dirs = {
        '.git', '__pycache__', 'venv', 'env', '.venv',
        'data', 'snapshots', 'packages', '.pytest_cache',
        '.idea', '.vscode', 'node_modules'
    }
    
    exclude_files = {
        '.gitignore', '.gitattributes', '.DS_Store',
        'Thumbs.db', '*.pyc', '*.pyo', '*.log',
        'package-lock.json', 'yarn.lock'
    }
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"lan_excel_editor_offline_v1.0.0_{timestamp}.zip"
    
    print(f"正在打包: {zip_filename}")
    print()
    
    # 创建 zip 文件
    file_count = 0
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # 排除文件
                if file in exclude_files:
                    continue
                if file.endswith(('.pyc', '.pyo', '.log')):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                    
                    # 显示进度（每 50 个文件）
                    if file_count % 50 == 0:
                        print(f"  已打包 {file_count} 个文件...")
                        
                except Exception as e:
                    print(f"  [警告] 跳过 {arcname}: {e}")
    
    # 获取文件大小
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print()
    print("=" * 60)
    print("  打包完成！")
    print("=" * 60)
    print()
    print(f"文件名: {zip_filename}")
    print(f"文件数: {file_count}")
    print(f"大小: {size_mb:.1f} MB")
    print()
    print("包含内容:")
    print("  [OK] Python 源码")
    print("  [OK] 前端库 (Handsontable, Socket.io)")
    print("  [OK] 启动脚本 (start.bat, start.py)")
    print("  [OK] 部署文档 (DEPLOY.md)")
    print()
    print("使用说明:")
    print("1. 将此 zip 文件复制到目标服务器")
    print("2. 解压到任意目录")
    print("3. 安装 Python 3.9+ (如果尚未安装)")
    print("4. 双击 start.bat 启动服务")
    print()
    
    return True

if __name__ == "__main__":
    success = create_offline_package()
    sys.exit(0 if success else 1)