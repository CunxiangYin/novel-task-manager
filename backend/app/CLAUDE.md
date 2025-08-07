# CLAUDE.md - Backend Application Code

## Overview
Core application code for the FastAPI backend service with async SQLAlchemy and WebSocket support.

## Module Structure
```
app/
├── api/                 # API Layer
│   ├── __init__.py        # Router aggregation
│   ├── tasks.py           # Task endpoints
│   └── websocket.py       # WebSocket handlers
├── models/             # Data Layer
│   ├── __init__.py        # Model exports
│   └── task.py            # Database models
├── schemas/            # Contract Layer
│   ├── __init__.py        # Schema exports
│   └── task.py            # Pydantic models
├── services/           # Business Layer
│   ├── __init__.py        # Service exports
│   └── task_processor.py  # Processing logic
├── utils/              # Utility Layer
│   ├── __init__.py        # Utility exports
│   └── file_handler.py    # File operations
├── config.py           # Configuration
├── database.py         # Database setup
└── main.py            # Application entry
```

## Layer Responsibilities

### API Layer (`/api`)
- HTTP endpoint definitions
- Request/response handling
- WebSocket connection management
- Input validation via Pydantic
- Error response formatting

### Model Layer (`/models`)
- SQLAlchemy ORM models
- Database table definitions
- Relationships and constraints
- Indexes and performance hints
- Migration compatibility

### Schema Layer (`/schemas`)
- Pydantic validation models
- Request/response contracts
- Data transformation rules
- API documentation generation
- Type safety enforcement

### Service Layer (`/services`)
- Business logic implementation
- Task processing workflows
- External service integration
- Transaction management
- Complex computations

### Utility Layer (`/utils`)
- Shared helper functions
- File system operations
- Data formatting utilities
- Common algorithms
- Third-party integrations

## Code Patterns

### Async Database Operations
```python
async def get_task(db: AsyncSession, task_id: str) -> Task:
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()
```

### Dependency Injection
```python
async def endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Use injected dependencies
    pass
```

### Background Tasks
```python
@router.post("/process")
async def process(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    background_tasks.add_task(
        process_heavy_task, 
        task_id
    )
    return {"status": "processing"}
```

### WebSocket Management
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)
```

## Database Patterns

### Model Definition
```python
class Task(Base):
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Fields with constraints
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    
    # Relationships
    logs = relationship(
        "TaskLog", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_status_priority", "status", "priority"),
    )
```

### Transaction Management
```python
async def create_task_with_logs(db: AsyncSession):
    async with db.begin():
        task = Task(...)
        db.add(task)
        
        log = TaskLog(task_id=task.id, ...)
        db.add(log)
        
        # Auto-commit on context exit
```

## Error Handling

### Custom Exceptions
```python
class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")
```

### Exception Handlers
```python
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": str(exc)}
    )
```

### Try-Catch Patterns
```python
try:
    result = await process_task(task_id)
except TaskProcessingError as e:
    await log_error(task_id, str(e))
    raise HTTPException(status_code=500, detail=str(e))
finally:
    await cleanup_resources()
```

## Configuration Management

### Settings Class
```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # API
    API_TITLE: str = "Novel Task Manager"
    API_VERSION: str = "1.0.0"
    
    # File handling
    MAX_FILE_SIZE: int = 10_485_760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".md"]
    
    class Config:
        env_file = ".env"
```

### Environment-Specific Config
```python
if os.getenv("ENVIRONMENT") == "production":
    settings = ProductionSettings()
else:
    settings = DevelopmentSettings()
```

## Testing Patterns

### Unit Tests
```python
@pytest.mark.asyncio
async def test_create_task():
    async with AsyncSession(engine) as db:
        task = await create_task(db, file_data)
        assert task.status == TaskStatus.PENDING
```

### Integration Tests
```python
async def test_upload_endpoint():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/api/v1/tasks/upload",
            files={"file": ("test.txt", b"content")}
        )
        assert response.status_code == 200
```

## Performance Optimization

### Query Optimization
```python
# Use select with specific columns
query = select(Task.id, Task.status).where(
    Task.status == TaskStatus.PENDING
)

# Use joinedload for relationships
query = select(Task).options(
    joinedload(Task.logs)
)
```

### Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_processing_config(task_type: str):
    # Expensive computation cached
    return config
```

### Connection Pooling
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Security Considerations

### Input Validation
- Always use Pydantic models
- Validate file types and sizes
- Sanitize user inputs
- Use parameterized queries

### Authentication Flow
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    # Verify token and return user
    pass
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"]
)
```

## Logging Best Practices

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "task_processed",
    task_id=task.id,
    duration_ms=duration,
    status=task.status
)
```

### Log Levels
- DEBUG: Detailed diagnostic info
- INFO: General information
- WARNING: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical failures

## Deployment Readiness

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "storage": await check_storage()
    }
```

### Graceful Shutdown
```python
@app.on_event("shutdown")
async def shutdown():
    await close_database_connections()
    await cleanup_temp_files()
```

### Monitoring Integration
```python
from prometheus_client import Counter, Histogram

task_counter = Counter(
    'tasks_total', 
    'Total number of tasks'
)
task_duration = Histogram(
    'task_duration_seconds',
    'Task processing duration'
)
```