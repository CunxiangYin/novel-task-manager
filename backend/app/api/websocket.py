from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set
import json
import asyncio

from app.database import get_db
from app.models import Task
from sqlalchemy import select

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_subscribers: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # Remove from all task subscriptions
        for task_id in list(self.task_subscribers.keys()):
            if client_id in self.task_subscribers[task_id]:
                self.task_subscribers[task_id].remove(client_id)
                if not self.task_subscribers[task_id]:
                    del self.task_subscribers[task_id]
    
    def subscribe_to_task(self, client_id: str, task_id: str):
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(client_id)
    
    def unsubscribe_from_task(self, client_id: str, task_id: str):
        if task_id in self.task_subscribers and client_id in self.task_subscribers[task_id]:
            self.task_subscribers[task_id].remove(client_id)
            if not self.task_subscribers[task_id]:
                del self.task_subscribers[task_id]
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
    
    async def broadcast_task_update(self, task_id: str, message: dict):
        if task_id in self.task_subscribers:
            message_text = json.dumps(message)
            disconnected_clients = []
            
            for client_id in self.task_subscribers[task_id]:
                if client_id in self.active_connections:
                    try:
                        await self.active_connections[client_id].send_text(message_text)
                    except:
                        disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.disconnect(client_id)

manager = ConnectionManager()

@router.websocket("/tasks/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time task updates"""
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "subscribe":
                task_id = message.get("task_id")
                if task_id:
                    manager.subscribe_to_task(client_id, task_id)
                    
                    # Send current task status
                    result = await db.execute(
                        select(Task).where(Task.id == task_id)
                    )
                    task = result.scalar_one_or_none()
                    
                    if task:
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "task_update",
                                "task_id": task_id,
                                "status": task.status.value,
                                "progress": task.progress,
                                "result_url": task.result_url,
                                "error_message": task.error_message
                            }),
                            client_id
                        )
            
            elif message["type"] == "unsubscribe":
                task_id = message.get("task_id")
                if task_id:
                    manager.unsubscribe_from_task(client_id, task_id)
            
            elif message["type"] == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    client_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)

async def notify_task_update(task_id: str, status: str, progress: int, 
                            result_url: str = None, error_message: str = None):
    """Send task update to all subscribed clients"""
    
    await manager.broadcast_task_update(
        task_id,
        {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "result_url": result_url,
            "error_message": error_message
        }
    )