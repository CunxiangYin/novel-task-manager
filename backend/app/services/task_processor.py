import asyncio
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Task, TaskLog, TaskResult
from app.models.task import TaskStatus, LogLevel
from app.api.websocket import notify_task_update

class TaskProcessor:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def process_task(self, task_id: str):
        """Process a single task"""
        try:
            # Update task status to processing
            await self.update_task_status(task_id, TaskStatus.PROCESSING)
            
            # Log start of processing
            await self.add_log(
                task_id, 
                LogLevel.INFO, 
                "Task processing started"
            )
            
            # Simulate processing with progress updates
            await self.simulate_processing(task_id)
            
            # Mark as completed
            await self.update_task_status(
                task_id, 
                TaskStatus.COMPLETED,
                result_url=f"/results/{task_id}"
            )
            
            # Log completion
            await self.add_log(
                task_id,
                LogLevel.INFO,
                "Task processing completed successfully"
            )
            
        except Exception as e:
            # Mark as failed
            await self.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=str(e)
            )
            
            # Log error
            await self.add_log(
                task_id,
                LogLevel.ERROR,
                f"Task processing failed: {str(e)}"
            )
    
    async def simulate_processing(self, task_id: str):
        """Simulate task processing with progress updates"""
        progress = 0
        
        while progress < 100:
            # Simulate work
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Update progress
            progress += random.randint(5, 20)
            progress = min(progress, 100)
            
            await self.update_task_progress(task_id, progress)
            
            # Send WebSocket notification
            await notify_task_update(
                task_id=task_id,
                status="processing",
                progress=progress
            )
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                                result_url: str = None, error_message: str = None):
        """Update task status in database"""
        
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(
                status=status,
                updated_at=datetime.utcnow()
            )
        )
        
        # Add conditional updates
        values = {"status": status, "updated_at": datetime.utcnow()}
        
        if status == TaskStatus.PROCESSING:
            values["started_at"] = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            values["completed_at"] = datetime.utcnow()
        
        if result_url:
            values["result_url"] = result_url
        if error_message:
            values["error_message"] = error_message
        
        stmt = update(Task).where(Task.id == task_id).values(**values)
        
        await self.db.execute(stmt)
        await self.db.commit()
        
        # Send WebSocket notification
        await notify_task_update(
            task_id=task_id,
            status=status.value,
            progress=100 if status == TaskStatus.COMPLETED else 0,
            result_url=result_url,
            error_message=error_message
        )
    
    async def update_task_progress(self, task_id: str, progress: int):
        """Update task progress"""
        
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(
                progress=progress,
                updated_at=datetime.utcnow()
            )
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def add_log(self, task_id: str, level: LogLevel, message: str, details: dict = None):
        """Add log entry for task"""
        
        log = TaskLog(
            task_id=task_id,
            log_level=level,
            message=message,
            details=details
        )
        
        self.db.add(log)
        await self.db.commit()