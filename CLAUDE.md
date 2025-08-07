# CLAUDE.md - Novel Task Manager Application

## Project Overview
A full-stack web application for managing novel processing tasks with real-time progress tracking and WebSocket updates. The application allows users to upload text files (novels), process them asynchronously, and monitor progress in real-time.

## Architecture
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + WebSocket
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: WebSocket for live progress updates

## Project Structure
```
novel_task_manager_app/
├── frontend/           # React frontend application
├── backend/           # FastAPI backend service
├── docs/             # Documentation and design files
└── tests/            # Integration tests
```

## Key Features
1. **File Upload System**: Drag-and-drop interface for uploading novel text files
2. **Task Queue Management**: Concurrent processing with configurable limits
3. **Real-time Updates**: WebSocket-based progress tracking
4. **Result Management**: Processed results with download links
5. **Statistics Dashboard**: Overall system metrics and task statistics

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python start_local.py  # Starts on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5174
```

## Testing
- Backend tests: `cd backend && python test_full_flow.py`
- WebSocket tests: `cd backend && python test_websocket.py`
- Frontend build: `cd frontend && npm run build`

## API Documentation
- API Docs: http://localhost:8000/docs
- WebSocket endpoint: ws://localhost:8000/api/v1/ws/tasks/{client_id}

## Database Schema
The application uses 5 main tables:
- `tasks`: Main task records
- `task_logs`: Processing logs
- `task_results`: Processing results
- `task_queue`: Queue management
- `file_storage`: File storage metadata

## Configuration
- Frontend config: `frontend/src/config/index.ts`
- Backend config: `backend/app/config.py`
- Environment variables: `backend/.env` (create from `.env.example`)

## Important Notes
1. The backend uses SQLite for local development, PostgreSQL for production
2. WebSocket connections auto-reconnect on disconnection
3. Maximum concurrent tasks is set to 3 by default
4. File size limit is 10MB by default
5. Supported file types: .txt, .md

## Common Commands
```bash
# Backend
python start_local.py          # Start backend server
python test_full_flow.py       # Test complete flow
python test_websocket.py       # Test WebSocket only

# Frontend
npm run dev                    # Development server
npm run build                  # Production build
npm run type-check            # TypeScript checking
```

## Troubleshooting
1. **Port conflicts**: Ensure ports 8000 (backend) and 5174 (frontend) are free
2. **Database errors**: Delete `test.db` and restart backend to reset
3. **WebSocket issues**: Check CORS settings in backend config
4. **Build errors**: Run `npm run type-check` to identify TypeScript issues