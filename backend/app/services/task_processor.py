import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Task, TaskLog, TaskResult
from app.models.task import TaskStatus, LogLevel
from app.api.websocket import notify_task_update
from app.config import settings

class TaskProcessor:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def process_task(self, task_id: str):
        """Process a single task with timeout monitoring"""
        try:
            # Update task status to processing
            await self.update_task_status(task_id, TaskStatus.PROCESSING)
            
            # Log start of processing
            await self.add_log(
                task_id, 
                LogLevel.INFO, 
                "Task processing started"
            )
            
            # Run processing with timeout
            try:
                await asyncio.wait_for(
                    self.simulate_processing(task_id),
                    timeout=settings.TASK_TIMEOUT_SECONDS
                )
                
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
                
            except asyncio.TimeoutError:
                # Task exceeded timeout
                await self.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error_message=f"Task exceeded maximum processing time of {settings.TASK_TIMEOUT_SECONDS // 60} minutes"
                )
                
                # Log timeout error
                await self.add_log(
                    task_id,
                    LogLevel.ERROR,
                    f"Task processing timed out after {settings.TASK_TIMEOUT_SECONDS // 60} minutes"
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
        start_time = datetime.utcnow()
        progress = 0
        
        # Get task to check if we need actual processing
        result = await self.db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise Exception(f"Task {task_id} not found")
        
        # Simulate realistic progress for a 30-minute task
        # Update every 30 seconds with smaller increments
        update_interval = 30  # seconds
        progress_increment = 3  # percent per update (~30 updates for 100%)
        
        while progress < 100:
            # Check if task was cancelled or failed externally
            await self.db.refresh(task)
            if task.status == TaskStatus.FAILED:
                return
            
            # Simulate work with realistic timing
            await asyncio.sleep(update_interval)
            
            # Update progress more realistically
            progress += progress_increment
            progress = min(progress, 100)
            
            # Calculate elapsed time
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Add processing stage information
            if progress < 20:
                stage_message = "Initializing and preparing data..."
            elif progress < 40:
                stage_message = "Analyzing content structure..."
            elif progress < 60:
                stage_message = "Processing main content..."
            elif progress < 80:
                stage_message = "Generating results..."
            else:
                stage_message = "Finalizing output..."
            
            await self.update_task_progress(task_id, progress)
            
            # Send WebSocket notification with more details
            await notify_task_update(
                task_id=task_id,
                status="processing",
                progress=progress
            )
            
            # Log progress at key milestones
            if progress in [25, 50, 75, 100]:
                await self.add_log(
                    task_id,
                    LogLevel.INFO,
                    f"Processing {progress}% complete - {stage_message}",
                    details={"elapsed_seconds": int(elapsed)}
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