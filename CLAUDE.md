# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack web application for managing novel text processing tasks with real-time progress tracking via WebSocket. Allows users to upload text files, process them asynchronously, and monitor progress in real-time.

## Architecture

- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + Zustand
- **Backend**: FastAPI + SQLAlchemy 2.0 (async) + WebSocket
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: WebSocket for live progress updates and task status

## Key Commands

### Frontend Development
```bash
cd frontend
npm install              # Install dependencies
npm run dev              # Start dev server (http://localhost:5174)
npm run build            # Production build
npm run type-check       # TypeScript type checking
npm run lint             # ESLint checking
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements_local.txt  # For development
python start_local.py    # Start server (http://localhost:8000)
```

### Testing
```bash
# Backend tests
cd backend
python test_full_flow.py    # Complete integration test
python test_websocket.py    # WebSocket functionality test
python test_task_update.py  # Task update tests
python test_timeout.py      # Timeout handling tests

# Frontend validation
cd frontend
npm run type-check          # TypeScript validation
npm run build               # Build validation
```

### Linting and Formatting
```bash
# Frontend
cd frontend
npm run lint                # ESLint
npm run type-check          # TypeScript checking

# Backend
cd backend
black .                     # Python formatter
flake8                      # Python linter
```

## Core Architecture

### Database Schema
The application uses 5 main tables managed by SQLAlchemy:
- `tasks`: Core task records with status tracking
- `task_logs`: Processing logs and debug information
- `task_results`: Processing outputs and download links
- `task_queue`: Queue management and worker assignment
- `file_storage`: File metadata and checksums

### API Structure
- **REST Endpoints**: `/api/v1/tasks/*` for CRUD operations
- **WebSocket**: `/api/v1/ws/tasks/{client_id}` for real-time updates
- **Statistics**: `/api/v1/tasks/statistics` for system metrics

### Task Processing Flow
1. File upload creates task with `status='pending'`
2. Task enters processing queue (max 3 concurrent)
3. Backend worker processes task, sending progress via WebSocket
4. On completion: `status='completed'` with result URL
5. On failure: `status='failed'` with error message

### WebSocket Protocol
```json
// Client -> Server
{"type": "subscribe", "task_id": "task-123"}
{"type": "unsubscribe", "task_id": "task-123"}
{"type": "ping"}

// Server -> Client
{"type": "task_update", "task_id": "task-123", "status": "processing", "progress": 50}
{"type": "pong"}
```

## Configuration

### Environment Variables
- Backend reads from `.env` file or environment
- Frontend uses Vite environment variables (`VITE_*` prefix)
- `start_local.py` auto-configures for local development

### Key Settings
- Max file size: 10MB (configurable)
- Supported formats: .txt, .md
- Max concurrent tasks: 3
- WebSocket auto-reconnect: 3 second delay

## Development Workflow

### Adding New Features
1. Backend: Add models in `app/models/`, schemas in `app/schemas/`, endpoints in `app/api/`
2. Frontend: Add components in `src/components/`, update store in `src/store/`
3. Run type checking and tests before committing

### State Management
- Frontend uses Zustand for global state (`src/store/novelTaskStore.ts`)
- Backend uses SQLAlchemy async sessions with connection pooling
- WebSocket connections managed by ConnectionManager class

### Error Handling
- Backend: Comprehensive try-catch with detailed logging
- Frontend: Error boundaries and fallback UI
- WebSocket: Auto-reconnection on disconnect
- Task processing: Retry mechanism with configurable limits

## Important Files

### Frontend
- `src/store/novelTaskStore.ts` - Main state management
- `src/hooks/useWebSocket.ts` - WebSocket connection logic
- `src/components/FileUpload.tsx` - Upload interface
- `src/config/index.ts` - Configuration settings

### Backend
- `app/main.py` - FastAPI application entry
- `app/api/tasks.py` - Task API endpoints
- `app/api/websocket.py` - WebSocket handlers
- `app/services/task_processor.py` - Processing logic
- `start_local.py` - Local development server

## API Documentation
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Common Issues

### Port Conflicts
Ensure ports 8000 (backend) and 5174 (frontend) are available

### Database Reset
```bash
cd backend
rm test.db  # Remove SQLite database
python start_local.py  # Recreate tables
```

### WebSocket Connection
Check CORS settings if WebSocket fails to connect. The `start_local.py` script includes "*" for development.

### Type Errors
Run `npm run type-check` in frontend to identify TypeScript issues before building.