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
# Get LAN IP for CORS
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    lan_ip = s.getsockname()[0]
    s.close()
except:
    lan_ip = "192.168.1.1"  # fallback

# Include both localhost and LAN IP in CORS origins
cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://localhost:3000",
    f"http://{lan_ip}:5173",
    f"http://{lan_ip}:5174",
    f"http://{lan_ip}:5175",
    f"http://{lan_ip}:3000",
    "http://192.168.0.0/16",  # Allow entire local network range
    "http://10.0.0.0/8",      # Allow entire local network range
    "http://172.16.0.0/12"    # Allow entire local network range
]
os.environ['CORS_ORIGINS'] = str(cors_origins)
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
    import socket
    from app.main import app
    
    # Get local network IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        # Try to get actual LAN IP (not loopback)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except:
        lan_ip = "Unable to detect"
    
    print("\n" + "="*50)
    print("Starting Novel Task Manager API (Local Mode)")
    print("="*50)
    print("\nAccess URLs:")
    print(f"  Local:   http://localhost:8000")
    print(f"  LAN:     http://{lan_ip}:8000")
    print(f"\nAPI Docs:")
    print(f"  Local:   http://localhost:8000/docs")
    print(f"  LAN:     http://{lan_ip}:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )
