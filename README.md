# 小说任务处理管理系统 (Novel Task Manager)

一个全栈Web应用，用于管理小说文本处理任务，支持文件上传、实时进度跟踪和WebSocket通信。

![Status](https://img.shields.io/badge/status-active-success.svg)
![React](https://img.shields.io/badge/React-19.0.0-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-3178C6?logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)

## 🎯 功能特性

- 📤 **文件上传系统**: 支持拖拽上传和批量处理
- 📊 **实时进度跟踪**: WebSocket实时更新处理进度
- 🎯 **任务队列管理**: 支持并发处理和任务优先级
- 📈 **统计仪表板**: 实时显示系统指标和任务统计
- 💾 **结果管理**: 处理结果存储和下载链接
- 🔄 **自动重连**: WebSocket断线自动重连机制

## 🏗️ 技术架构

### 前端技术栈
- **框架**: React 19 + TypeScript 5.6
- **构建工具**: Vite 6.0
- **样式**: Tailwind CSS 3.4
- **状态管理**: Zustand 5.0
- **拖拽**: @dnd-kit
- **图标**: Lucide React

### 后端技术栈
- **框架**: FastAPI 0.104
- **ORM**: SQLAlchemy 2.0 (Async)
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **WebSocket**: FastAPI WebSocket
- **验证**: Pydantic 2.5

## 📁 项目结构

```
novel_task_manager_app/
├── frontend/                # React前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── store/         # Zustand状态管理
│   │   ├── config/        # 配置文件
│   │   └── types/         # TypeScript类型
│   └── dist/              # 生产构建输出
├── backend/                # FastAPI后端服务
│   ├── app/
│   │   ├── api/          # API端点
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic模式
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── uploads/          # 上传文件存储
│   └── test.db          # SQLite数据库
└── docs/                # 项目文档
```

## 🚀 快速开始

### 前置要求

- Node.js 18+ 和 npm
- Python 3.12+
- Git

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd novel_task_manager_app
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements_local.txt
# 或者如果是生产环境:
pip install -r requirements.txt
```

#### 3. 前端设置

```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install
```

### 启动应用

#### 开发模式

**启动后端服务:**
```bash
cd backend
python start_local.py
# 服务运行在 http://localhost:8000
# API文档: http://localhost:8000/docs
```

**启动前端开发服务器:**
```bash
cd frontend
npm run dev
# 应用运行在 http://localhost:5174
```

#### 生产构建

```bash
cd frontend
npm run build
# 构建输出在 frontend/dist/
```

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Components**: Modular React components for UI
- **State Management**: Zustand for global state
- **Real-time Updates**: WebSocket integration
- **Styling**: Tailwind CSS for responsive design

### Backend (FastAPI + PostgreSQL)
- **API Layer**: RESTful endpoints with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Processing**: Async task queue system
- **WebSocket**: Real-time progress updates

### Database Schema
- **tasks**: Main task information
- **task_logs**: Processing logs
- **task_results**: Processing results
- **task_queue**: Queue management
- **file_storage**: File storage information

## 🔧 Configuration

### Frontend Environment Variables
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws
VITE_USE_MOCK_API=false
```

### Backend Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/novel_task_manager
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173
MAX_CONCURRENT_TASKS=3
```

## 📝 API Documentation

### Main Endpoints

#### Tasks
- `POST /api/v1/tasks/upload` - Upload file and create task
- `GET /api/v1/tasks` - List tasks with pagination
- `GET /api/v1/tasks/{id}` - Get task details
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/retry` - Retry failed task

#### Statistics
- `GET /api/v1/tasks/statistics` - Get task statistics

#### WebSocket
- `WS /api/v1/ws/tasks/{client_id}` - Real-time updates

## 🧪 测试

### 运行测试

```bash
# 后端测试
cd backend
python test_full_flow.py   # 完整流程测试
python test_websocket.py   # WebSocket测试

# 前端类型检查
cd frontend
npm run type-check         # TypeScript类型检查
```

### 生产构建

```bash
# 构建前端
cd frontend
npm run build

# 构建后端Docker镜像
cd backend
docker build -t novel-task-manager-api .
```

## 🐳 Docker部署

```bash
# 使用Docker Compose构建和运行
cd backend
docker-compose up --build
```

## 📊 任务处理流程

1. **上传** - 用户通过拖拽上传文本文件
2. **排队** - 任务加入处理队列
3. **处理** - 后端处理文件（最多3个并发）
4. **进度** - 通过WebSocket发送实时更新
5. **完成** - 结果可供下载

## 🛠️ 技术栈详情

### 前端技术
- React 19.0.0
- TypeScript 5.6.2
- Vite 6.0.5
- Tailwind CSS 3.4.17
- Zustand 5.0.2
- Lucide React
- @dnd-kit/sortable
- date-fns

### 后端技术
- FastAPI 0.104.1
- SQLAlchemy 2.0 (异步)
- PostgreSQL 16 (生产)
- SQLite (开发)
- Pydantic 2.5
- Python 3.12+
- aiofiles
- python-multipart

## 📈 性能特性

- 支持多任务并发处理
- WebSocket实时更新，无需轮询
- 数据库索引优化查询速度
- 连接池提升可扩展性
- SHA256哈希实现文件去重

## 🔒 安全特性

- 文件类型验证
- 文件大小限制（默认10MB）
- ORM防止SQL注入
- CORS配置保护
- Pydantic输入验证

## 🤝 贡献指南

1. Fork本仓库
2. 创建功能分支
3. 提交你的修改
4. 运行测试
5. 提交Pull Request

## 📄 许可证

MIT License - 详见LICENSE文件

## 🙏 致谢

- FastAPI团队提供的优秀Web框架
- React团队提供的前端库
- 所有开源贡献者

## 📞 支持

如有问题请:
- 在GitHub上创建Issue
- 查看`/docs`目录中的文档
- 访问API文档 http://localhost:8000/docs

---

用 ❤️ 构建 | 最后更新: 2025年8月