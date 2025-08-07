import os
import hashlib
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import settings

def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

async def save_upload_file(content: bytes, original_filename: str, task_id: str) -> str:
    """Save uploaded file to storage"""
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectory based on date
    date_dir = upload_dir / datetime.now().strftime("%Y%m%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(original_filename)[1]
    stored_filename = f"{task_id}{file_ext}"
    file_path = date_dir / stored_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return str(file_path)

async def read_file_content(file_path: str) -> Optional[bytes]:
    """Read file content from storage"""
    
    if not os.path.exists(file_path):
        return None
    
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    return content

def delete_file(file_path: str) -> bool:
    """Delete file from storage"""
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_file_info(file_path: str) -> dict:
    """Get file information"""
    
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    return {
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "modified_at": datetime.fromtimestamp(stat.st_mtime),
        "path": file_path
    }