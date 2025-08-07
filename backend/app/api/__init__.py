from fastapi import APIRouter
from app.api import tasks, websocket, database

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(database.router, prefix="/database", tags=["database"])