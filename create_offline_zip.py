import os
import zipfile
import shutil
from pathlib import Path

print("=" * 60)
print("  创建完整离线安装包")
print("=" * 60)
print()

# 检查依赖包
packages_dir = Path("packages")
if not packages_dir.exists():
    print("[错误] packages/ 目录不存在")
    exit(1)

whl_files = list(packages_dir.glob("*.whl"))
print(f"[OK] 找到 {len(whl_files)} 个依赖包")

# 创建 zip
zip_name = "lan_excel_editor_offline_v1.0.0.zip"
print(f"正在创建: {zip_name}")
print()

# 定义要包含的内容
include_files = [
    "app.py", "config.py", "utils.py", "start.bat", "start.py",
    "requirements.txt", "README.md", "DEPLOY.md", "RELEASE_NOTES.md",
    "STRUCTURE.md", "COLLAB_CURSOR.md", "build_package.py",
    "download_deps.py", "build_complete_offline.py"
]

include_dirs = ["handlers", "services", "models", "templates", "static", "tasks", "packages"]

exclude_patterns = [".git", "__pycache__", ".pyc", ".pyo", ".log", ".DS_Store", "Thumbs.db"]

file_count = 0

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    # 添加单个文件
    for file in include_files:
        if os.path.exists(file):
            zf.write(file, file)
            file_count += 1
            print(f"  [文件] {file}")
    
    # 添加目录
    for dir_name in include_dirs:
        if os.path.exists(dir_name):
            for root, dirs, files in os.walk(dir_name):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]
                
                for file in files:
                    if any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.log']):
                        continue
                    if file in ['.DS_Store', 'Thumbs.db']:
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = file_path
                    zf.write(file_path, arcname)
                    file_count += 1
            
            print(f"  [目录] {dir_name}")

# 显示结果
zip_size = os.path.getsize(zip_name) / (1024 * 1024)

print()
print("=" * 60)
print("  打包完成！")
print("=" * 60)
print()
print(f"文件名: {zip_name}")
print(f"文件数: {file_count}")
print(f"大小: {zip_size:.1f} MB")
print()
print("包含:")
print("  - Python 源代码")
print("  - 前端库 (已本地化)")
print(f"  - {len(whl_files)} 个 Python 依赖包")
print("  - 启动脚本和文档")
print()
print("使用方法:")
print("1. 解压到任意目录")
print("2. 安装 Python 3.9+")
print("3. 双击 start.bat 启动")