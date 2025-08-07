#!/usr/bin/env python3
"""
Local development server starter for testing without Docker
Uses SQLite for database and in-memory task queue
"""

import os
import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

# Override database URL for local development - MUST be before imports
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['DATABASE_SYNC_URL'] = 'sqlite:///./test.db'

# Override CORS settings to proper JSON format
os.environ['CORS_ORIGINS'] = '["http://localhost:5173","http://localhost:5174","http://localhost:3000"]'
os.environ['ALLOWED_EXTENSIONS'] = '[".txt",".md"]'

# Create necessary directories
Path('./uploads').mkdir(exist_ok=True)

# Now import after environment is set
from app.database import Base, sync_engine
from app.models import *  # Import all models

def init_db():
    """Initialize SQLite database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Start the server
    import uvicorn
    from app.main import app
    
    print("\n" + "="*50)
    print("Starting Novel Task Manager API (Local Mode)")
    print("="*50)
    print("\nAPI URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )