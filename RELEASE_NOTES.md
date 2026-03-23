# 局域网多人 Excel 编辑器 v1.0.0 发布说明

## 🎉 版本信息

- **版本**: v1.0.0
- **发布日期**: 2024-03-20
- **状态**: 稳定版

## ✨ 主要功能

### 核心功能
- ✅ 按文件隔离的多人实时协作编辑
- ✅ WebSocket 实时同步（单元格修改、样式变更）
- ✅ 文件管理系统（文件夹、新建、上传、下载、重命名、移动、删除）
- ✅ 版本快照与回滚（自动保存历史版本）
- ✅ 只读权限控制

### 样式功能
- ✅ 单元格样式编辑（粗体、斜体、下划线）
- ✅ 字体大小调整（10px-24px）
- ✅ 文字颜色（12种常用颜色）
- ✅ 背景颜色（16种常用颜色）
- ✅ 对齐方式（左对齐、居中、右对齐）
- ✅ 样式持久化（实时保存到 JSON，随版本快照备份）

### 协作功能
- ✅ 实时显示其他用户选中位置（带颜色边框）
- ✅ 用户名标签显示
- ✅ 平滑动画过渡
- ✅ 多 Sheet 支持

### 高级功能
- ✅ 查找和替换（Ctrl+F）
- ✅ 撤销/重做（Ctrl+Z / Ctrl+Y）
- ✅ 常用快捷键支持
- ✅ 完全离线可用（前端库已本地化）

## 📦 离线包内容

### 包含的文件
- 完整的 Python 源码
- 本地化的前端库（Handsontable、Socket.io）
- 启动脚本（Windows 批处理 + Python 脚本）
- 部署文档
- 依赖清单

### 系统要求
- Windows 10/11 / Windows Server 2016+
- Python 3.9+
- 2 GB RAM
- 500 MB 磁盘空间
- 局域网环境

## 🚀 快速开始

### Windows 用户
1. 安装 Python 3.9+（勾选 "Add Python to PATH"）
2. 解压 `lan_excel_editor_offline.zip`
3. 双击 `start.bat`
4. 浏览器访问 http://localhost:5000

### Linux/Mac 用户
```bash
cd lan_excel_editor
pip install -r requirements.txt
python app.py
```

## 📁 项目结构

```
lan_excel_editor/
├── start.bat              # Windows 启动脚本
├── start.py               # 跨平台启动器
├── DEPLOY.md              # 详细部署文档
├── README.md              # 功能说明
├── requirements.txt       # 依赖清单
├── app.py                 # 主程序入口
├── config.py              # 配置
├── static/                # 前端资源
│   ├── css/
│   └── js/
├── templates/             # HTML 模板
├── handlers/              # 请求处理器
├── services/              # 业务逻辑
├── models/                # 数据模型
└── data/                  # 数据目录（运行时创建）
    ├── files/             # Excel 文件
    ├── meta/              # 元数据
    ├── snapshots/         # 版本快照
    └── styles/            # 样式文件
```

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python / Flask / Flask-SocketIO / gevent |
| 实时通信 | WebSocket (Socket.io) |
| Excel 读写 | openpyxl |
| 前端表格 | Handsontable |
| 会话隔离 | Socket.IO Room |

## 📝 更新日志

### v1.0.0 (2024-03-20)
- 首次发布稳定版
- 完成多人协作编辑功能
- 添加本地样式编辑
- 实现样式持久化（混合方案）
- 添加查找替换、撤销重做
- 完善离线部署方案

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

---

**下载地址**: https://github.com/bilipoi/lanExcelWebTool/releases/tag/v1.0.0

**使用问题?** 查看 DEPLOY.md 或提交 Issue