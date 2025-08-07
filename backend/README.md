# Novel Task Manager Backend

FastAPI backend service for the Novel Task Manager application.

最后更新: 2025年8月

## Features

- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Async/await support throughout
- ✅ WebSocket support for real-time updates
- ✅ File upload and processing
- ✅ Task queue management
- ✅ Database migrations with Alembic
- ✅ Docker support for easy deployment

## Setup

### 1. Local Development Setup (SQLite)

```bash
# For local development with SQLite (no Docker required)
python start_local.py
```

### Production Setup (PostgreSQL)

```bash
# Start PostgreSQL with Docker
docker-compose up -d
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for local development
pip install -r requirements_local.txt

# Or for production
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

### 4. Initialize Database

```bash
# Create database tables
python init_db.py

# Or use Alembic migrations
alembic upgrade head
```

### 5. Run the Server

```bash
# Local development with SQLite
python start_local.py

# Or production mode with PostgreSQL
python app/main.py

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tasks

- `POST /api/v1/tasks/upload` - Upload a file and create a task
- `GET /api/v1/tasks/` - List tasks with pagination
- `GET /api/v1/tasks/{task_id}` - Get task details
- `PATCH /api/v1/tasks/{task_id}` - Update task status
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `POST /api/v1/tasks/{task_id}/retry` - Retry a failed task
- `GET /api/v1/tasks/statistics` - Get task statistics

### WebSocket

- `WS /api/v1/ws/tasks/{client_id}` - WebSocket for real-time updates

## Database Schema

The database consists of 5 main tables:

1. **tasks** - Main task information
2. **task_logs** - Processing logs
3. **task_results** - Processing results
4. **task_queue** - Queue management
5. **file_storage** - File storage information

## Development

### Run Tests

```bash
# Full integration test
python test_full_flow.py

# WebSocket test
python test_websocket.py

# Unit tests (if available)
pytest tests/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Formatting

```bash
# Format code
black app/

# Check linting
flake8 app/
```

## Docker Deployment

```bash
# Build image
docker build -t novel-task-manager-api .

# Run container
docker run -p 8000:8000 --env-file .env novel-task-manager-api
```

## Environment Variables

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ORIGINS` - Allowed CORS origins
- `MAX_FILE_SIZE` - Maximum upload file size
- `MAX_CONCURRENT_TASKS` - Maximum concurrent processing tasks

## Architecture

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── utils/         # Utility functions
│   ├── config.py      # Configuration
│   ├── database.py    # Database setup
│   └── main.py        # Application entry point
├── alembic/           # Database migrations
├── tests/             # Test files
├── uploads/           # Uploaded files
└── docker-compose.yml # Docker services
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Run tests and linting
5. Submit a pull request

## Recent Updates

- Added SQLite support for local development
- Improved WebSocket connection handling
- Added comprehensive test scripts
- Updated to latest FastAPI and SQLAlchemy versions
- Enhanced error handling and logging

## License

MIT