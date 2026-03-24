# 局域网多人 Excel 编辑器 v1.0.0

基于 Flask + WebSocket 的局域网多人实时协作 Excel 编辑工具。支持**按文件隔离的多人会话**，打开同一文件的用户实时协作编辑，不同文件之间互不干扰。

**特点**：完全离线可用，无需互联网连接。

---

## ✨ 主要功能

### 🎯 核心特性
- **文件级会话隔离**：打开文件 A 的用户只能看到/编辑文件 A，与文件 B 的用户互不干扰
- **多人实时协作**：同一文件内的用户实时同步单元格修改
- **完全离线**：所有依赖已本地化，纯局域网运行
- **自动保存**：智能检测变更，仅在有变更时创建版本快照

### 📝 文件管理
- ✅ 文件夹分类管理（创建、重命名、删除）
- ✅ 新建空白 Excel 文件
- ✅ 上传本地 xlsx 文件
- ✅ 下载文件到本地
- ✅ 文件移动和重命名

### 🎨 样式编辑（v1.0.0 新增）
- ✅ **文字样式**：加粗、斜体、下划线
- ✅ **字体大小**：10px ~ 24px
- ✅ **文字颜色**：12 种常用颜色
- ✅ **背景颜色**：16 种常用颜色
- ✅ **对齐方式**：左对齐、居中、右对齐
- ✅ **样式持久化**：保存到 JSON 文件，随版本快照备份

### 🔍 高级功能（v1.0.0 新增）
- ✅ **查找替换**（Ctrl+F）
- ✅ **撤销/重做**（Ctrl+Z / Ctrl+Y）
- ✅ **快捷键支持**（Ctrl+S 保存、Ctrl+B/I/U 样式）

### 👥 协作功能
- ✅ **实时显示其他用户**：彩色边框 + 用户名标签标识选中位置
- ✅ **独立颜色**：每个用户分配不同颜色（18 色循环）
- ✅ **平滑动画**：用户移动选中位置时平滑过渡

### 💾 版本管理
- ✅ **智能快照**：仅当内容变更时创建快照
- ✅ **最多 20 个版本**：自动清理最旧版本
- ✅ **一键回滚**：选择任意历史版本恢复
- ✅ **样式备份**：版本快照包含样式数据

---

## 🚀 快速开始

### 方式 1：完整离线包（推荐）

1. 下载 `lan_excel_editor_offline_v1.0.0.zip`
2. 解压到任意目录
3. **安装 Python 3.9+**（勾选 "Add Python to PATH"）
4. 双击 `start.bat` 启动
5. 浏览器访问 `http://localhost:5000`

### 方式 2：源码运行

```bash
pip install -r requirements.txt
python app.py
```

---

## 📁 项目结构

```
lan_excel_editor/
├── app.py                 # 主入口
├── config.py              # 配置
├── utils.py               # 工具函数
├── requirements.txt       # 依赖清单
├── start.bat              # Windows 启动脚本 ⭐
├── DEPLOY.md              # 详细部署文档 ⭐
│
├── models/
│   └── session.py         # 文件会话管理
│
├── services/              # 业务逻辑
│   ├── file_tree.py       # 文件树
│   ├── file_service.py    # 文件操作
│   ├── folder_service.py  # 文件夹操作
│   ├── snapshot_service.py # 版本快照
│   ├── meta_service.py    # 元数据
│   └── style_service.py   # 样式持久化 ⭐
│
├── handlers/              # 请求处理
│   ├── http_handlers.py   # HTTP API
│   └── websocket_handlers.py # WebSocket
│
├── tasks/
│   └── auto_save.py       # 自动保存
│
├── static/                # 前端资源 ⭐
│   ├── css/handsontable.full.min.css
│   └── js/
│       ├── handsontable.full.min.js
│       └── socket.io.min.js
│
└── templates/
    └── index.html         # 前端页面
```

**⭐ 标注为新增或关键文件**

---

## 💻 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python / Flask / Flask-SocketIO / gevent |
| 实时通信 | WebSocket (Socket.io) |
| Excel 读写 | openpyxl |
| 前端表格 | Handsontable |
| 会话隔离 | Socket.IO Room |

---

## 📖 详细文档

- **部署指南**: 查看 [DEPLOY.md](DEPLOY.md)
- **系统要求**: Windows 10+/Linux/Mac, Python 3.9+, 2GB RAM
- **端口**: 默认 5000（可在 config.py 修改）

---

## 🔄 更新日志

### v1.0.0 (2024-03-20)
- ✅ 首次发布稳定版
- ✅ 本地样式编辑（粗体、颜色、对齐等）
- ✅ 样式持久化（混合方案：JSON + 快照备份）
- ✅ 查找替换、撤销重做
- ✅ 完全离线部署方案

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

---

**下载**: [Releases](https://github.com/bilipoi/lanExcelWebTool/releases)