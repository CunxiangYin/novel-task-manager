from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import hashlib
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Task, TaskLog, TaskResult, FileStorage
from app.schemas.task import (
    TaskResponse, TaskListResponse, TaskStatistics,
    TaskUpdate, FileUploadResponse, TaskStatus
)
from app.config import settings
from app.services.task_processor import TaskProcessor
from app.utils.file_handler import save_upload_file, calculate_file_hash

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file and create a new task"""
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file_content = await file.read()
    file_size = len(file_content)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Calculate file hash for deduplication
    file_hash = calculate_file_hash(file_content)
    
    # Check if file already exists
    existing_task = await db.execute(
        select(Task).where(Task.file_hash == file_hash)
    )
    if existing_task.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="This file has already been uploaded"
        )
    
    # Generate task ID
    task_id = f"task-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:9]}"
    
    # Save file to storage
    stored_file_path = await save_upload_file(file_content, file.filename, task_id)
    
    # Create task in database
    task = Task(
        id=task_id,
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type or "text/plain",
        file_hash=file_hash,
        status=TaskStatus.PENDING,
        progress=0,
        uploaded_at=datetime.utcnow()
    )
    
    # Create file storage record
    file_storage = FileStorage(
        task_id=task_id,
        storage_type="local",
        storage_path=stored_file_path,
        original_name=file.filename,
        stored_name=os.path.basename(stored_file_path),
        content_type=file.content_type,
        file_size=file_size,
        checksum=file_hash
    )
    
    db.add(task)
    db.add(file_storage)
    await db.commit()
    
    # Start processing in background
    processor = TaskProcessor(db)
    background_tasks.add_task(processor.process_task, task_id)
    
    return FileUploadResponse(
        task_id=task_id,
        file_name=file.filename,
        file_size=file_size,
        status="pending"
    )

@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    sort_by: str = Query("uploaded_at", regex="^(uploaded_at|file_name|status)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of tasks with pagination and filtering"""
    
    # Build query
    query = select(Task)
    
    # Apply status filter
    if status:
        query = query.where(Task.status == status)
    
    # Apply sorting
    sort_column = getattr(Task, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    count_query = select(func.count()).select_from(Task)
    if status:
        count_query = count_query.where(Task.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/statistics", response_model=TaskStatistics)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Get task statistics"""
    
    # Get counts by status
    result = await db.execute(
        select(
            func.count(Task.id).label("total"),
            func.count(Task.id).filter(Task.status == TaskStatus.PENDING).label("pending"),
            func.count(Task.id).filter(Task.status == TaskStatus.PROCESSING).label("processing"),
            func.count(Task.id).filter(Task.status == TaskStatus.COMPLETED).label("completed"),
            func.count(Task.id).filter(Task.status == TaskStatus.FAILED).label("failed")
        )
    )
    stats = result.first()
    
    # Calculate average processing time for completed tasks
    # Get all completed tasks with valid timestamps
    completed_tasks_result = await db.execute(
        select(Task.started_at, Task.completed_at).where(
            and_(
                Task.status == TaskStatus.COMPLETED,
                Task.started_at.isnot(None),
                Task.completed_at.isnot(None)
            )
        )
    )
    completed_tasks = completed_tasks_result.all()
    
    # Calculate average processing time in Python (works with both SQLite and PostgreSQL)
    avg_processing_time = None
    if completed_tasks:
        processing_times = []
        for started_at, completed_at in completed_tasks:
            # Calculate time difference in milliseconds
            time_diff = (completed_at - started_at).total_seconds() * 1000
            # Only include positive values (sanity check)
            if time_diff > 0:
                processing_times.append(time_diff)
        
        if processing_times:
            avg_processing_time = round(sum(processing_times) / len(processing_times), 2)
    
    # Calculate success rate
    success_rate = None
    if stats.total > 0:
        success_rate = round((stats.completed / stats.total) * 100, 2)
    
    return TaskStatistics(
        total=stats.total or 0,
        pending=stats.pending or 0,
        processing=stats.processing or 0,
        completed=stats.completed or 0,
        failed=stats.failed or 0,
        avg_processing_time_ms=avg_processing_time,
        success_rate=success_rate
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific task by ID"""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.model_validate(task)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update task status or progress"""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Update timestamps based on status
    if task_update.status == TaskStatus.PROCESSING and not task.started_at:
        task.started_at = datetime.utcnow()
    elif task_update.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        task.completed_at = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task and its associated data"""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete associated files
    file_storage_result = await db.execute(
        select(FileStorage).where(FileStorage.task_id == task_id)
    )
    file_storages = file_storage_result.scalars().all()
    
    for storage in file_storages:
        if storage.storage_type == "local" and os.path.exists(storage.storage_path):
            os.remove(storage.storage_path)
    
    # Delete task (cascades to related tables)
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted successfully"}

@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed task"""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatus.FAILED, TaskStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail="Only failed or completed tasks can be retried"
        )
    
    # Reset task status
    task.status = TaskStatus.PENDING
    task.progress = 0
    task.error_message = None
    task.result_url = None
    task.started_at = None
    task.completed_at = None
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    
    # Start processing in background
    processor = TaskProcessor(db)
    background_tasks.add_task(processor.process_task, task_id)
    
    await db.refresh(task)
    return TaskResponse.model_validate(task)