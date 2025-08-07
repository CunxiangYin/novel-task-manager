#!/usr/bin/env python3
"""
LAN-accessible server starter for local network testing
Allows access from any device on the same network
"""

import os
import sys
import socket
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

# Override database URL for local development
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['DATABASE_SYNC_URL'] = 'sqlite:///./test.db'

# Get LAN IP address
def get_lan_ip():
    """Get the LAN IP address of this machine"""
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
        return "127.0.0.1"

lan_ip = get_lan_ip()

# Configure CORS to allow all origins for LAN access
# WARNING: This is for development only! Don't use in production!
os.environ['CORS_ORIGINS'] = '["*"]'
os.environ['ALLOWED_EXTENSIONS'] = '[".txt",".md"]'

# Create necessary directories
Path('./uploads').mkdir(exist_ok=True)

# Import after environment is set
from app.database import Base, sync_engine
from app.models import *

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
    
    print("\n" + "="*60)
    print("Starting Novel Task Manager API (LAN Access Mode)")
    print("="*60)
    print("\n⚠️  WARNING: This server is accessible from your local network!")
    print("    Only use this for testing. Not for production!")
    print("\nAccess URLs:")
    print(f"  This machine:    http://localhost:8000")
    print(f"  Other devices:   http://{lan_ip}:8000")
    print(f"\nAPI Documentation:")
    print(f"  This machine:    http://localhost:8000/docs")
    print(f"  Other devices:   http://{lan_ip}:8000/docs")
    print("\nFrontend Access:")
    print(f"  Update frontend config to use: http://{lan_ip}:8000/api/v1")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )