# 项目结构说明

重构后的项目采用分层架构，各功能模块分离：

```
lan_excel_editor/
├── app.py                      # 主入口，Flask/SocketIO 初始化
├── config.py                   # 配置（目录、常量、颜色池）
├── utils.py                    # 工具函数（路径、哈希）
│
├── models/                     # 数据模型层
│   ├── __init__.py
│   └── session.py             # FileSession 类、全局会话管理
│
├── services/                   # 业务逻辑层
│   ├── __init__.py
│   ├── file_tree.py           # 文件树构建
│   ├── folder_service.py      # 文件夹操作（创建、重命名、删除）
│   ├── file_service.py        # 文件操作（创建、重命名、移动、删除、权限）
│   ├── snapshot_service.py    # 版本快照（创建、列出、恢复）
│   └── meta_service.py        # 元数据管理（权限存储）
│
├── handlers/                   # 请求处理层
│   ├── __init__.py
│   ├── http_handlers.py       # HTTP 路由（REST API）
│   └── websocket_handlers.py  # WebSocket 事件处理
│
├── tasks/                      # 后台任务
│   └── auto_save.py           # 自动保存循环
│
└── templates/
    └── index.html             # 前端页面
```

## 架构说明

### 1. 配置层 (config.py)
- 所有配置集中管理：目录路径、常量、颜色池
- 便于修改和扩展

### 2. 工具层 (utils.py)
- 通用工具函数：路径处理、哈希计算
- 无副作用，可被各层调用

### 3. 模型层 (models/session.py)
- **FileSession**：单个文件的状态管理
  - 表格数据缓存
  - 在线用户列表（含颜色、选中状态）
  - 数据哈希（变更检测）
  - 只读状态
- **全局状态**：file_sessions、user_current_file

### 4. 服务层 (services/)
- **file_tree.py**：递归构建文件树，包含在线人数统计
- **folder_service.py**：文件夹的 CRUD 操作
- **file_service.py**：文件的 CRUD 操作 + 权限管理
- **snapshot_service.py**：版本快照的创建、列出、恢复
- **meta_service.py**：JSON 文件读写，存储权限元数据

### 5. 处理层 (handlers/)
- **http_handlers.py**：处理 HTTP 请求，调用服务层
- **websocket_handlers.py**：处理 WebSocket 事件，实现实时协作

### 6. 任务层 (tasks/)
- **auto_save.py**：后台定时任务，自动保存有变更的文件

## 模块依赖关系

```
app.py (入口)
├── config.py (配置)
├── utils.py (工具)
├── models/session.py (状态)
│   ├── config
│   ├── utils
│   └── services/meta_service.py
├── services/* (业务逻辑)
│   ├── config
│   ├── utils
│   └── models/session.py
├── handlers/* (请求处理)
│   ├── app (socketio)
│   ├── config
│   ├── utils
│   ├── models/session.py
│   └── services/*
└── tasks/* (后台任务)
    ├── config
    ├── models/session.py
    └── services/snapshot_service.py
```

## 优势

1. **单一职责**：每个文件只负责一个功能模块
2. **可维护性**：修改某功能只需找对应文件
3. **可测试性**：各层可独立测试
4. **可扩展性**：新增功能只需添加新模块
5. **清晰的依赖关系**：避免循环依赖

## 启动方式不变

```bash
python app.py
```

所有模块会自动导入，无需修改启动命令。
