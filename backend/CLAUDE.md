# CLAUDE.md - Backend API Service

## Overview
FastAPI backend service for the Novel Task Manager application with async SQLAlchemy, WebSocket support, and task processing.

## Tech Stack
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL (prod) / SQLite (dev)
- **WebSocket**: FastAPI WebSocket
- **Validation**: Pydantic 2.5
- **Async**: Python asyncio
- **Migration**: Alembic

## Project Structure
```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD operations
│   │   └── websocket.py    # WebSocket handlers
│   ├── models/           # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── task.py         # Database models
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   └── task.py         # Request/response models
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   └── task_processor.py  # Task processing logic
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   └── file_handler.py    # File operations
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection
│   └── main.py          # Application entry point
├── uploads/             # Uploaded files storage
├── alembic/            # Database migrations
├── tests/              # Test files
├── requirements.txt    # Python dependencies
├── start_local.py     # Local development server
├── test_websocket.py  # WebSocket test script
└── test_full_flow.py  # Integration test script
```

## Database Schema

### Tables
1. **tasks** - Main task records
   - id (PK): Task identifier
   - file_name, file_size, file_type
   - status: pending/processing/completed/failed
   - progress: 0-100
   - timestamps: uploaded_at, started_at, completed_at

2. **task_logs** - Processing logs
   - id (PK): Log entry ID
   - task_id (FK): Reference to task
   - log_level: info/warning/error/debug
   - message, details, created_at

3. **task_results** - Processing results
   - id (PK): Result ID
   - task_id (FK): Reference to task
   - result_file_path, summary
   - quality_score, confidence_score

4. **task_queue** - Queue management
   - id (PK): Queue entry ID
   - task_id (FK): Reference to task
   - queue_position, assigned_worker
   - retry_count, timeout_seconds

5. **file_storage** - File metadata
   - id (PK): Storage ID
   - task_id (FK): Reference to task
   - storage_type, storage_path
   - checksum, expires_at

## API Endpoints

### Task Management
- `POST /api/v1/tasks/upload` - Upload file and create task
- `GET /api/v1/tasks/` - List tasks with pagination
- `GET /api/v1/tasks/{task_id}` - Get task details
- `PATCH /api/v1/tasks/{task_id}` - Update task status
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `GET /api/v1/tasks/statistics` - Get statistics

### WebSocket
- `WS /api/v1/ws/tasks/{client_id}` - Real-time updates

### WebSocket Message Types
```json
// Subscribe to task
{"type": "subscribe", "task_id": "task-123"}

// Unsubscribe from task
{"type": "unsubscribe", "task_id": "task-123"}

// Ping/Pong for keepalive
{"type": "ping"}
{"type": "pong"}

// Task update (server -> client)
{
  "type": "task_update",
  "task_id": "task-123",
  "status": "processing",
  "progress": 50,
  "result_url": null,
  "error_message": null
}
```

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
DATABASE_SYNC_URL=postgresql://user:pass@localhost/dbname
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5174"]
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=[".txt", ".md"]
```

### Local Development
```python
# start_local.py automatically sets:
DATABASE_URL=sqlite+aiosqlite:///./test.db
DATABASE_SYNC_URL=sqlite:///./test.db
```

## Task Processing Flow
1. File upload creates task with status='pending'
2. Task added to processing queue
3. Background worker picks up task
4. Status changes to 'processing'
5. Progress updates sent via WebSocket
6. On completion, status='completed' with result_url
7. On error, status='failed' with error_message

## Development Commands
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start local server (with SQLite)
python start_local.py

# Run tests
python test_websocket.py    # Test WebSocket
python test_full_flow.py    # Full integration test

# Database migrations (if using Alembic)
alembic init alembic
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

## Testing

### WebSocket Test
```bash
python test_websocket.py
# Options:
# 1. Test connection and subscription
# 2. Simulate task processing
```

### Integration Test
```bash
python test_full_flow.py
# Options:
# 1. Single task flow
# 2. Multiple concurrent tasks
```

## Performance Considerations
1. **Connection Pooling**: Configured for PostgreSQL
2. **Async Operations**: All DB operations are async
3. **Background Tasks**: Processing runs in background
4. **WebSocket Management**: Connection manager for efficiency
5. **File Handling**: Chunked reading for large files

## Security
1. File type validation
2. File size limits
3. CORS configuration
4. Input validation with Pydantic
5. SQL injection protection via SQLAlchemy

## Error Handling
- Comprehensive try-catch blocks
- Detailed error logging
- Graceful WebSocket disconnection
- Task retry mechanism
- Timeout management

## Monitoring
- Task statistics endpoint
- Processing time tracking
- Success rate calculation
- WebSocket connection tracking
- Detailed logging system

## Future Enhancements
1. Redis for task queue
2. Celery for distributed processing
3. S3/Cloud storage integration
4. Authentication & authorization
5. Rate limiting
6. Batch processing API
7. Export/Import functionality
8. Admin dashboard API