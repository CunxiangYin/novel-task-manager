import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models import Task, TaskLog
from app.models.task import TaskStatus, LogLevel
from app.api.websocket import notify_task_update
from app.config import settings
from app.database import async_session_maker


class TaskMonitor:
    """Monitor running tasks and enforce timeout limits"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every minute
    
    async def start(self):
        """Start the task monitor background process"""
        self.running = True
        while self.running:
            try:
                await self.check_timeouts()
            except Exception as e:
                print(f"Error in task monitor: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the task monitor"""
        self.running = False
    
    async def check_timeouts(self):
        """Check for tasks that have exceeded timeout"""
        async with async_session_maker() as db:
            try:
                # Calculate timeout threshold
                timeout_threshold = datetime.utcnow() - timedelta(seconds=settings.TASK_TIMEOUT_SECONDS)
                
                # Find tasks that are processing and started before timeout threshold
                result = await db.execute(
                    select(Task).where(
                        and_(
                            Task.status == TaskStatus.PROCESSING,
                            Task.started_at.isnot(None),
                            Task.started_at < timeout_threshold
                        )
                    )
                )
                timed_out_tasks = result.scalars().all()
                
                for task in timed_out_tasks:
                    # Calculate how long the task has been running
                    elapsed_seconds = (datetime.utcnow() - task.started_at).total_seconds()
                    
                    # Update task status to failed
                    task.status = TaskStatus.FAILED
                    task.error_message = f"Task exceeded maximum processing time of {settings.TASK_TIMEOUT_SECONDS // 60} minutes"
                    task.completed_at = datetime.utcnow()
                    task.updated_at = datetime.utcnow()
                    
                    # Add timeout log
                    timeout_log = TaskLog(
                        task_id=task.id,
                        log_level=LogLevel.ERROR,
                        message=f"Task automatically failed due to timeout after {int(elapsed_seconds // 60)} minutes",
                        details={"elapsed_seconds": int(elapsed_seconds), "timeout_seconds": settings.TASK_TIMEOUT_SECONDS}
                    )
                    db.add(timeout_log)
                    
                    # Send WebSocket notification
                    await notify_task_update(
                        task_id=task.id,
                        status=TaskStatus.FAILED.value,
                        progress=task.progress,
                        error_message=task.error_message
                    )
                    
                    print(f"Task {task.id} timed out after {int(elapsed_seconds // 60)} minutes")
                
                if timed_out_tasks:
                    await db.commit()
                    
            except Exception as e:
                print(f"Error checking timeouts: {e}")
                await db.rollback()


# Global task monitor instance
task_monitor = TaskMonitor()