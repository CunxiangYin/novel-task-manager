# Project Structure

## 📁 Directory Layout

```
novel_task_manager_app/
│
├── 📁 frontend/                    # Frontend主目录 (React + TypeScript)
│   ├── 📁 src/                     # 源代码
│   │   ├── 📁 components/          # React组件
│   │   │   ├── FileUpload.tsx     # 文件上传组件
│   │   │   ├── TaskList.tsx       # 任务列表组件
│   │   │   ├── TaskItem.tsx       # 任务项组件
│   │   │   └── TaskStats.tsx      # 任务统计组件
│   │   ├── 📁 store/               # 状态管理 (Zustand)
│   │   │   └── novelTaskStore.ts  # 任务状态存储
│   │   ├── 📁 types/               # TypeScript类型定义
│   │   │   └── novelTask.ts       # 任务类型定义
│   │   ├── 📁 services/            # API服务
│   │   │   └── api.ts             # API调用封装
│   │   ├── 📁 hooks/               # React Hooks
│   │   │   └── useWebSocket.ts    # WebSocket Hook
│   │   ├── 📁 config/              # 配置
│   │   │   └── index.ts           # 应用配置
│   │   ├── App.tsx                 # 主应用组件
│   │   ├── main.tsx                # 应用入口
│   │   └── index.css               # 全局样式
│   ├── 📁 dist/                    # 生产构建输出
│   ├── 📁 node_modules/            # Node依赖
│   ├── 📄 package.json             # 前端依赖配置
│   ├── 📄 tsconfig.json            # TypeScript配置
│   ├── 📄 vite.config.ts           # Vite配置
│   ├── 📄 tailwind.config.js       # Tailwind CSS配置
│   ├── 📄 postcss.config.js        # PostCSS配置
│   ├── 📄 index.html               # HTML入口
│   ├── 📄 .env.example             # 环境变量示例
│   └── 📄 README.md                # 前端文档
│
├── 📁 backend/                     # 后端主目录 (FastAPI + Python)
│   ├── 📁 app/                     # 应用代码
│   │   ├── 📁 api/                 # API端点
│   │   │   ├── tasks.py           # 任务相关API
│   │   │   └── websocket.py       # WebSocket端点
│   │   ├── 📁 models/              # 数据库模型
│   │   │   └── task.py            # 任务数据模型
│   │   ├── 📁 schemas/             # Pydantic模式
│   │   │   └── task.py            # 任务数据验证
│   │   ├── 📁 services/            # 业务逻辑
│   │   │   └── task_processor.py  # 任务处理服务
│   │   ├── 📁 utils/               # 工具函数
│   │   │   └── file_handler.py    # 文件处理工具
│   │   ├── 📄 config.py            # 配置管理
│   │   ├── 📄 database.py          # 数据库连接
│   │   └── 📄 main.py              # FastAPI应用入口
│   ├── 📁 alembic/                 # 数据库迁移
│   │   ├── 📄 env.py               # Alembic环境配置
│   │   └── 📄 script.py.mako       # 迁移脚本模板
│   ├── 📁 uploads/                 # 上传文件存储
│   ├── 📄 requirements.txt         # Python依赖
│   ├── 📄 docker-compose.yml       # Docker服务配置
│   ├── 📄 init_db.py              # 数据库初始化脚本
│   ├── 📄 alembic.ini             # Alembic配置
│   ├── 📄 .env.example            # 环境变量示例
│   ├── 📄 run_dev.sh              # 开发启动脚本
│   └── 📄 README.md               # 后端文档
│
├── 📁 docs/                        # 项目文档
│   └── 📄 database-design.md      # 数据库设计文档
│
├── 📄 README.md                    # 项目主文档
├── 📄 package.json                 # 项目脚本配置
├── 📄 .gitignore                  # Git忽略文件
└── 📄 PROJECT_STRUCTURE.md        # 本文件
```

## 🔧 主要技术栈

### Frontend (前端)
- **框架**: React 19 + TypeScript 5
- **构建工具**: Vite 6
- **样式**: Tailwind CSS 3
- **状态管理**: Zustand
- **图标**: Lucide React
- **拖拽**: @dnd-kit
- **日期处理**: date-fns

### Backend (后端)
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库**: PostgreSQL 16
- **缓存**: Redis
- **迁移**: Alembic
- **异步**: asyncio + asyncpg
- **验证**: Pydantic

## 📋 功能模块

### 1. 文件上传模块
- 位置: `frontend/src/components/FileUpload.tsx`
- 功能: 拖拽上传、批量上传、文件验证

### 2. 任务管理模块
- 前端: `frontend/src/components/TaskList.tsx`, `TaskItem.tsx`
- 后端: `backend/app/api/tasks.py`
- 功能: CRUD操作、状态管理、进度跟踪

### 3. 实时通信模块
- 前端: `frontend/src/hooks/useWebSocket.ts`
- 后端: `backend/app/api/websocket.py`
- 功能: WebSocket连接、实时进度更新

### 4. 数据存储模块
- 模型: `backend/app/models/task.py`
- 数据库: PostgreSQL (5个主表)
- 功能: 数据持久化、查询优化

## 🚀 快速启动

```bash
# 1. 启动后端
cd backend
python -m venv venv         # 创建虚拟环境
source venv/bin/activate    # 激活虚拟环境
pip install -r requirements_local.txt  # 安装依赖
python start_local.py       # 启动本地服务器（SQLite）

# 2. 启动前端
cd ../frontend
npm install                 # 安装依赖
npm run dev                 # 启动开发服务器
```

## 📝 API端点

- `POST   /api/v1/tasks/upload`     - 上传文件
- `GET    /api/v1/tasks`            - 获取任务列表
- `GET    /api/v1/tasks/{id}`       - 获取任务详情
- `PATCH  /api/v1/tasks/{id}`       - 更新任务
- `DELETE /api/v1/tasks/{id}`       - 删除任务
- `POST   /api/v1/tasks/{id}/retry` - 重试任务
- `GET    /api/v1/tasks/statistics` - 获取统计信息
- `WS     /api/v1/ws/tasks/{id}`    - WebSocket连接

## 🔗 访问地址

- **前端应用**: http://localhost:5174
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/api/v1/ws/tasks/{client_id}

## 🔍 最新更新

### 2025年8月更新
- 前端升级到React 19 + Vite 6
- 后端支持SQLite本地开发
- 新增WebSocket自动重连机制
- 优化任务并发处理逻辑
- 完善测试脚本和文档

---

*最后更新: 2025年8月*