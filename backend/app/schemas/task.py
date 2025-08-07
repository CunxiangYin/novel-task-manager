from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskBase(BaseModel):
    file_name: str
    file_size: int
    file_type: str = "text/plain"
    priority: int = 0
    extra_data: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result_url: Optional[str] = None
    error_message: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    status: TaskStatus
    progress: int
    uploaded_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    
class TaskStatistics(BaseModel):
    total: int
    pending: int
    processing: int
    completed: int
    failed: int
    avg_processing_time_ms: Optional[float] = None
    success_rate: Optional[float] = None

class TaskProgressUpdate(BaseModel):
    task_id: str
    progress: int = Field(..., ge=0, le=100)
    message: Optional[str] = None

class FileUploadResponse(BaseModel):
    task_id: str
    file_name: str
    file_size: int
    status: str
    message: str = "File uploaded successfully"

class TaskLogEntry(BaseModel):
    task_id: str
    log_level: str
    message: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskResultResponse(BaseModel):
    task_id: str
    summary: Optional[str] = None
    processing_time_ms: Optional[int] = None
    tokens_processed: Optional[int] = None
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    result_file_url: Optional[str] = None
    
    class Config:
        from_attributes = True