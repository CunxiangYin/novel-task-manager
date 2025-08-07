from sqlalchemy import (
    Column, String, Integer, BigInteger, Text, Boolean,
    DateTime, ForeignKey, Enum, DECIMAL, JSON, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"

class StorageType(str, enum.Enum):
    LOCAL = "local"
    S3 = "s3"
    OSS = "oss"

class Task(Base):
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), default="text/plain")
    file_hash = Column(String(64), index=True)
    
    # Task status
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    progress = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Result information
    result_url = Column(Text)
    error_message = Column(Text)
    
    # User information
    user_id = Column(String(50), index=True)
    session_id = Column(String(100), index=True)
    
    # Extra data
    extra_data = Column(JSON)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")
    result = relationship("TaskResult", back_populates="task", uselist=False, cascade="all, delete-orphan")
    queue_entry = relationship("TaskQueue", back_populates="task", uselist=False, cascade="all, delete-orphan")
    file_storage = relationship("FileStorage", back_populates="task", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="chk_progress"),
        Index("idx_tasks_status_priority", "status", "priority"),
        Index("idx_tasks_uploaded_at", "uploaded_at"),
    )

class TaskLog(Base):
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    log_level = Column(Enum(LogLevel), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    
    # Relationships
    task = relationship("Task", back_populates="logs")

class TaskResult(Base):
    __tablename__ = "task_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Result file information
    result_file_path = Column(Text)
    result_file_size = Column(BigInteger)
    result_file_type = Column(String(50))
    
    # Processing statistics
    processing_time_ms = Column(Integer)
    tokens_processed = Column(Integer)
    
    # Result data
    summary = Column(Text)
    full_content = Column(Text)
    
    # Quality metrics
    quality_score = Column(DECIMAL(3, 2))
    confidence_score = Column(DECIMAL(3, 2))
    
    # Extra data
    extra_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="result")

class TaskQueue(Base):
    __tablename__ = "task_queue"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Queue management
    queue_position = Column(Integer, nullable=False, index=True)
    assigned_worker = Column(String(100), index=True)
    assigned_at = Column(DateTime(timezone=True))
    
    # Retry mechanism
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True))
    
    # Timeout control
    timeout_seconds = Column(Integer, default=300)
    expires_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="queue_entry")

class FileStorage(Base):
    __tablename__ = "file_storage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Storage location
    storage_type = Column(Enum(StorageType), nullable=False)
    storage_path = Column(Text, nullable=False)
    storage_url = Column(Text)
    
    # File information
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    content_type = Column(String(100))
    file_size = Column(BigInteger, nullable=False)
    checksum = Column(String(64))
    
    # Status
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), index=True)
    
    # Relationships
    task = relationship("Task", back_populates="file_storage")