# API Endpoints Documentation

## Base URL
- Local: `http://localhost:8000`
- API Prefix: `/api/v1`

## Task Management Endpoints

### Upload File and Create Task
```
POST /api/v1/tasks/upload
Content-Type: multipart/form-data
Body: file (binary)
Response: { "task_id": "task-TIMESTAMP-HASH", "file_name": "...", "file_size": ..., "status": "pending" }
```

### Update Task Status
```
PATCH /api/v1/tasks/{task_id}
Content-Type: application/json
Body: { "status": "processing|completed|failed", "progress": 0-100, "error_message": "..." }

Example:
PATCH /api/v1/tasks/task-1754556928-12a41dbec
Body: { "status": "processing", "progress": 50 }
```

**Important**: The task_id must be the complete ID in format `task-TIMESTAMP-HASH`, not just the timestamp.

### Get Task Details
```
GET /api/v1/tasks/{task_id}
Response: Task object with current status, progress, etc.
```

### List All Tasks
```
GET /api/v1/tasks/
Query params: page, page_size, status, sort_by, order
```

### Get Statistics
```
GET /api/v1/tasks/statistics
Response: { "total": ..., "pending": ..., "processing": ..., "completed": ..., "failed": ... }
```

### Delete Task
```
DELETE /api/v1/tasks/{task_id}
```

### Retry Failed Task
```
POST /api/v1/tasks/{task_id}/retry
```

## WebSocket Endpoint

### Real-time Task Updates
```
WS /api/v1/ws/tasks/{client_id}
```

Messages:
- Subscribe: `{"type": "subscribe", "task_id": "task-TIMESTAMP-HASH"}`
- Unsubscribe: `{"type": "unsubscribe", "task_id": "task-TIMESTAMP-HASH"}`
- Task Update (server->client): `{"type": "task_update", "task_id": "...", "status": "...", "progress": ...}`

## Common Issues

### 404 Not Found on PATCH
If you get a 404 when trying to update task status, check:
1. The task_id is complete (e.g., `task-1754556928-12a41dbec` not just `1754556928`)
2. The endpoint includes `/api/v1/` prefix
3. The task exists in the database

### Correct API Call Example
```python
import httpx

# Correct
task_id = "task-1754556928-12a41dbec"
url = f"http://localhost:8000/api/v1/tasks/{task_id}"
data = {"status": "processing", "progress": 25}
response = httpx.patch(url, json=data)

# Incorrect (will get 404)
task_id = "1754556928"  # Missing prefix and hash
url = f"http://localhost:8000/api/task/{task_id}"  # Wrong path
```