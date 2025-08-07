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
import json
import socket

# Get LAN IP for CORS
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
    "*"  # Allow all origins for development
]
os.environ['CORS_ORIGINS'] = json.dumps(cors_origins)
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
    def get_lan_ip():
        try:
            # Get all network interfaces
            import subprocess
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            # Look for 192.168.x.x or 10.x.x.x addresses
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'inet' and i + 1 < len(parts):
                            ip = parts[i + 1]
                            # Prefer common LAN IP ranges
                            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                                return ip
            
            # Fallback to socket method
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    lan_ip = get_lan_ip()
    
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
