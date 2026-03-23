#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局域网多人 Excel 编辑器 - 启动器
支持 Windows/Linux/Mac，自动检查环境并启动服务
"""

import os
import sys
import subprocess
import platform

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    END = '\033[0m'

def print_banner():
    """打印启动横幅"""
    print(f"{Colors.GREEN}{'='*50}{Colors.END}")
    print(f"{Colors.GREEN}  局域网多人 Excel 编辑器 - 离线版{Colors.END}")
    print(f"{Colors.GREEN}{'='*50}{Colors.END}")
    print()

def check_python():
    """检查 Python 版本"""
    print(f"{Colors.YELLOW}正在检查 Python 环境...{Colors.END}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"{Colors.RED}[错误] Python 版本过低，需要 3.9+，当前 {version.major}.{version.minor}{Colors.END}")
        print(f"{Colors.GRAY}请访问 https://www.python.org/downloads/ 下载最新版{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}[OK] Python {version.major}.{version.minor}.{version.micro}{Colors.END}")
    return True

def setup_venv():
    """设置虚拟环境"""
    venv_dir = "venv"
    
    if os.path.exists(venv_dir):
        print(f"{Colors.GREEN}[OK] 虚拟环境已存在{Colors.END}")
        return True
    
    print(f"{Colors.YELLOW}首次运行，正在创建虚拟环境...{Colors.END}")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print(f"{Colors.GREEN}[OK] 虚拟环境创建成功{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[错误] 创建虚拟环境失败: {e}{Colors.END}")
        return False

def install_deps():
    """安装依赖"""
    print(f"{Colors.YELLOW}正在安装依赖（离线模式）...{Colors.END}")
    
    # 确定 pip 路径
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        python_path = os.path.join("venv", "Scripts", "python.exe")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    # 尝试离线安装
    packages_dir = "packages"
    if os.path.exists(packages_dir) and os.listdir(packages_dir):
        try:
            result = subprocess.run(
                [pip_path, "install", "--no-index", "--find-links", packages_dir, "-r", "requirements.txt"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}[OK] 依赖安装成功（离线模式）{Colors.END}")
                return python_path
        except:
            pass
    
    # 离线失败，尝试在线安装
    print(f"{Colors.YELLOW}[警告] 离线安装失败，尝试在线安装...{Colors.END}")
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print(f"{Colors.GREEN}[OK] 依赖安装成功（在线模式）{Colors.END}")
        return python_path
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[错误] 依赖安装失败: {e}{Colors.END}")
        print(f"{Colors.GRAY}请确保有网络连接，或手动运行:{Colors.END}")
        print(f"{Colors.GRAY}  pip install -r requirements.txt{Colors.END}")
        return None

def start_server(python_path):
    """启动服务"""
    print()
    print(f"{Colors.GREEN}{'='*50}{Colors.END}")
    print(f"{Colors.GREEN}  服务启动中...{Colors.END}")
    print(f"{Colors.GREEN}{'='*50}{Colors.END}")
    print()
    print(f"{Colors.CYAN}访问地址:{Colors.END}")
    print(f"  - 本机:    http://localhost:5000")
    print(f"  - 局域网:  http://[服务器IP]:5000")
    print()
    print(f"{Colors.GRAY}按 Ctrl+C 停止服务{Colors.END}")
    print()
    
    try:
        subprocess.run([python_path, "app.py"])
    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}服务已停止{Colors.END}")

def main():
    """主函数"""
    print_banner()
    
    # 检查 Python
    if not check_python():
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 设置虚拟环境
    if not setup_venv():
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 安装依赖
    python_path = install_deps()
    if not python_path:
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 启动服务
    start_server(python_path)

if __name__ == "__main__":
    main()