from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, delete
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database import get_db
from app.models import Task, TaskLog, TaskResult, TaskQueue, FileStorage
from app.models.task import TaskStatus
from app.schemas.database import (
    DatabaseStats, TableInfo, QueryResult, 
    DeleteResult, CleanupResult
)

router = APIRouter()

@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats(db: AsyncSession = Depends(get_db)):
    """Get overall database statistics"""
    
    # Get table counts
    tasks_count = await db.scalar(select(func.count(Task.id)))
    logs_count = await db.scalar(select(func.count(TaskLog.id)))
    results_count = await db.scalar(select(func.count(TaskResult.id)))
    queue_count = await db.scalar(select(func.count(TaskQueue.id)))
    storage_count = await db.scalar(select(func.count(FileStorage.id)))
    
    # Get task status distribution
    status_distribution = {}
    for status in TaskStatus:
        count = await db.scalar(
            select(func.count(Task.id)).where(Task.status == status)
        )
        status_distribution[status.value] = count
    
    # Get database size (SQLite specific)
    try:
        result = await db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
        db_size = result.scalar() or 0
    except:
        db_size = 0
    
    # Get recent activity
    recent_tasks = await db.scalar(
        select(func.count(Task.id)).where(
            Task.uploaded_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        )
    )
    
    return DatabaseStats(
        total_tasks=tasks_count or 0,
        total_logs=logs_count or 0,
        total_results=results_count or 0,
        total_queue_items=queue_count or 0,
        total_files=storage_count or 0,
        status_distribution=status_distribution,
        database_size_bytes=db_size,
        tasks_today=recent_tasks or 0
    )

@router.get("/tables", response_model=List[TableInfo])
async def get_tables_info(db: AsyncSession = Depends(get_db)):
    """Get information about all database tables"""
    
    tables_info = []
    
    # Define tables and their models
    table_models = [
        ("tasks", Task),
        ("task_logs", TaskLog),
        ("task_results", TaskResult),
        ("task_queue", TaskQueue),
        ("file_storage", FileStorage)
    ]
    
    for table_name, model in table_models:
        # Get row count
        count = await db.scalar(select(func.count()).select_from(model))
        
        # Get columns info
        columns = []
        for column in model.__table__.columns:
            columns.append({
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable,
                "primary_key": column.primary_key,
                "foreign_key": bool(column.foreign_keys)
            })
        
        tables_info.append(TableInfo(
            name=table_name,
            row_count=count or 0,
            columns=columns
        ))
    
    return tables_info

@router.get("/query/{table_name}", response_model=QueryResult)
async def query_table(
    table_name: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Query data from a specific table"""
    
    # Map table names to models
    table_map = {
        "tasks": Task,
        "task_logs": TaskLog,
        "task_results": TaskResult,
        "task_queue": TaskQueue,
        "file_storage": FileStorage
    }
    
    if table_name not in table_map:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    model = table_map[table_name]
    
    # Get total count
    total_count = await db.scalar(select(func.count()).select_from(model))
    
    # Get data with pagination
    query = select(model).offset(offset).limit(limit)
    
    # Add ordering for better consistency
    if hasattr(model, 'created_at'):
        query = query.order_by(model.created_at.desc())
    elif hasattr(model, 'uploaded_at'):
        query = query.order_by(model.uploaded_at.desc())
    elif hasattr(model, 'id'):
        query = query.order_by(model.id.desc())
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    # Convert to dict format
    data = []
    for row in rows:
        row_dict = {}
        for column in model.__table__.columns:
            value = getattr(row, column.name)
            # Convert datetime to string for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            # Convert enum to string
            elif hasattr(value, 'value'):
                value = value.value
            row_dict[column.name] = value
        data.append(row_dict)
    
    return QueryResult(
        table_name=table_name,
        total_count=total_count or 0,
        count=len(data),
        offset=offset,
        limit=limit,
        data=data
    )

@router.delete("/cleanup/logs", response_model=CleanupResult)
async def cleanup_old_logs(
    days_old: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Delete old task logs"""
    
    cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
    
    # Count logs to delete
    count_query = select(func.count(TaskLog.id)).where(TaskLog.created_at < cutoff_date)
    count = await db.scalar(count_query)
    
    # Delete old logs
    if count > 0:
        delete_query = delete(TaskLog).where(TaskLog.created_at < cutoff_date)
        await db.execute(delete_query)
        await db.commit()
    
    return CleanupResult(
        table_name="task_logs",
        deleted_count=count or 0,
        message=f"Deleted {count} logs older than {days_old} days"
    )

@router.delete("/cleanup/failed", response_model=CleanupResult)
async def cleanup_failed_tasks(
    days_old: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Delete old failed tasks and their associated data"""
    
    cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
    
    # Find failed tasks to delete
    failed_tasks = await db.execute(
        select(Task).where(
            Task.status == TaskStatus.FAILED,
            Task.uploaded_at < cutoff_date
        )
    )
    tasks_to_delete = failed_tasks.scalars().all()
    
    deleted_count = 0
    for task in tasks_to_delete:
        # Delete associated file storage
        file_storage = await db.execute(
            select(FileStorage).where(FileStorage.task_id == task.id)
        )
        for storage in file_storage.scalars():
            # Delete physical file if exists
            import os
            if storage.storage_type == "local" and os.path.exists(storage.storage_path):
                try:
                    os.remove(storage.storage_path)
                except:
                    pass
        
        # Delete task (cascades to related tables)
        await db.delete(task)
        deleted_count += 1
    
    if deleted_count > 0:
        await db.commit()
    
    return CleanupResult(
        table_name="tasks",
        deleted_count=deleted_count,
        message=f"Deleted {deleted_count} failed tasks older than {days_old} days"
    )

@router.post("/vacuum")
async def vacuum_database(db: AsyncSession = Depends(get_db)):
    """Vacuum the database to reclaim space (SQLite specific)"""
    
    try:
        # Note: VACUUM cannot be run inside a transaction
        await db.execute(text("VACUUM"))
        await db.commit()
        
        # Get new database size
        result = await db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
        new_size = result.scalar() or 0
        
        return {
            "success": True,
            "message": "Database vacuumed successfully",
            "database_size_bytes": new_size
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Vacuum failed: {str(e)}"
        }

@router.delete("/task/{task_id}", response_model=DeleteResult)
async def delete_specific_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific task and all its associated data"""
    
    # Find the task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    
    # Delete associated file if exists
    file_storage = await db.execute(
        select(FileStorage).where(FileStorage.task_id == task_id)
    )
    for storage in file_storage.scalars():
        import os
        if storage.storage_type == "local" and os.path.exists(storage.storage_path):
            try:
                os.remove(storage.storage_path)
            except:
                pass
    
    # Delete task (cascades to related tables)
    await db.delete(task)
    await db.commit()
    
    return DeleteResult(
        success=True,
        deleted_id=task_id,
        message=f"Task '{task_id}' and all associated data deleted successfully"
    )