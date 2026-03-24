#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整离线包构建工具
下载所有依赖并打包
"""

import os
import sys
import subprocess
import zipfile
from datetime import datetime

def download_dependencies():
    """下载所有 Python 依赖包"""
    print("=" * 60)
    print("  下载 Python 依赖包")
    print("=" * 60)
    print()
    
    packages_dir = "packages"
    if not os.path.exists(packages_dir):
        os.makedirs(packages_dir)
        print(f"[OK] 创建目录: {packages_dir}")
    
    print("正在下载依赖包（需要联网）...")
    print("这可能需要几分钟，请耐心等待...")
    print()
    
    # 使用 pip download 下载所有依赖
    result = subprocess.run(
        [sys.executable, "-m", "pip", "download", "-r", "requirements.txt", "-d", packages_dir, "--only-binary=:all:"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[错误] 下载失败:")
        print(result.stderr)
        return False
    
    # 统计下载的包
    packages = [f for f in os.listdir(packages_dir) if f.endswith(('.whl', '.tar.gz'))]
    print(f"[OK] 成功下载 {len(packages)} 个依赖包")
    print()
    
    # 显示前10个包
    for i, pkg in enumerate(sorted(packages)[:10], 1):
        print(f"  {i}. {pkg}")
    if len(packages) > 10:
        print(f"  ... 还有 {len(packages)-10} 个包")
    print()
    
    return True

def create_offline_package():
    """创建完整离线安装包"""
    print("=" * 60)
    print("  创建离线安装包")
    print("=" * 60)
    print()
    
    # 检查当前目录
    if not os.path.exists("app.py"):
        print("[错误] 请在项目根目录运行此脚本")
        return False
    
    # 定义排除项
    exclude_dirs = {'.git', '__pycache__', 'venv', 'env', '.venv', 'data', 'snapshots', 'temp_package'}
    exclude_files = {'.gitignore', '.gitattributes', '.DS_Store', 'Thumbs.db'}
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_filename = f"lan_excel_editor_complete_offline_v1.0.0_{timestamp}.zip"
    
    print(f"正在打包: {zip_filename}")
    print()
    
    file_count = 0
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. 打包源码文件
        print("步骤 1/2: 打包源码...")
        for root, dirs, files in os.walk('.'):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                if file.endswith(('.pyc', '.pyo', '.log')):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                except Exception as e:
                    print(f"  [跳过] {arcname}: {e}")
        
        print(f"  [OK] 源码文件: {file_count} 个")
        
        # 2. 打包依赖包
        print("步骤 2/2: 打包依赖...")
        if os.path.exists("packages"):
            for pkg_file in os.listdir("packages"):
                if pkg_file.endswith(('.whl', '.tar.gz')):
                    pkg_path = os.path.join("packages", pkg_file)
                    zipf.write(pkg_path, f"packages/{pkg_file}")
                    file_count += 1
            
            pkg_count = len([f for f in os.listdir("packages") if f.endswith(('.whl', '.tar.gz'))])
            print(f"  [OK] 依赖包: {pkg_count} 个")
        else:
            print("  [警告] packages/ 目录不存在，请先运行下载")
    
    # 获取文件大小
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print()
    print("=" * 60)
    print("  打包完成！")
    print("=" * 60)
    print()
    print(f"文件名: {zip_filename}")
    print(f"总文件数: {file_count}")
    print(f"大小: {size_mb:.1f} MB")
    print()
    print("包含内容:")
    print("  [OK] Python 源代码")
    print("  [OK] 前端库 (已本地化)")
    print("  [OK] Python 依赖包 (.whl 文件)")
    print("  [OK] 启动脚本和文档")
    print()
    print("使用说明:")
    print("1. 解压到目标服务器")
    print("2. 安装 Python 3.9+")
    print("3. 双击 start.bat 启动")
    print()
    
    return True

def main():
    """主函数"""
    print()
    
    # 步骤 1: 下载依赖
    if not download_dependencies():
        print("[错误] 依赖下载失败，请检查网络连接")
        input("\n按回车键退出...")
        return 1
    
    # 步骤 2: 创建包
    if not create_offline_package():
        print("[错误] 打包失败")
        input("\n按回车键退出...")
        return 1
    
    print("[OK] 所有步骤完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())