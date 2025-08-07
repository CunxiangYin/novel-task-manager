#!/usr/bin/env python3
"""
Helper script for updating task status via API
This can be used by external services to properly update task status
"""

import httpx
import json
from typing import Optional, Literal

class TaskUpdater:
    """Helper class for updating task status"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        
    def update_task_status(
        self,
        task_id: str,
        status: Optional[Literal["pending", "processing", "completed", "failed"]] = None,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        result_url: Optional[str] = None
    ) -> dict:
        """
        Update task status
        
        Args:
            task_id: Full task ID (e.g., "task-1754556928-12a41dbec")
            status: New status
            progress: Progress percentage (0-100)
            error_message: Error message if failed
            result_url: Result URL if completed
            
        Returns:
            Response data or error dict
        """
        
        # Validate task_id format
        if not task_id.startswith("task-"):
            print(f"Warning: Task ID '{task_id}' doesn't start with 'task-'. It might be incomplete.")
            # Try to construct full ID if only timestamp is provided
            if task_id.isdigit():
                print(f"Error: Only timestamp provided ({task_id}). Full task ID required (e.g., task-{task_id}-HASH)")
                return {"error": "Invalid task ID format"}
        
        # Build update data
        update_data = {}
        if status is not None:
            update_data["status"] = status
        if progress is not None:
            update_data["progress"] = min(100, max(0, progress))  # Clamp to 0-100
        if error_message is not None:
            update_data["error_message"] = error_message
        if result_url is not None:
            update_data["result_url"] = result_url
            
        if not update_data:
            return {"error": "No update data provided"}
        
        # Make API call
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}"
        
        try:
            response = httpx.patch(url, json=update_data, timeout=10.0)
            
            if response.status_code == 200:
                print(f"✓ Task {task_id} updated successfully")
                return response.json()
            elif response.status_code == 404:
                print(f"✗ Task {task_id} not found")
                return {"error": f"Task not found: {task_id}"}
            else:
                print(f"✗ Failed to update task: {response.status_code}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"✗ Error updating task: {e}")
            return {"error": str(e)}
    
    def mark_processing(self, task_id: str, progress: int = 0):
        """Mark task as processing with initial progress"""
        return self.update_task_status(task_id, status="processing", progress=progress)
    
    def mark_completed(self, task_id: str, result_url: str):
        """Mark task as completed with result URL"""
        return self.update_task_status(task_id, status="completed", progress=100, result_url=result_url)
    
    def mark_failed(self, task_id: str, error_message: str):
        """Mark task as failed with error message"""
        return self.update_task_status(task_id, status="failed", error_message=error_message)
    
    def update_progress(self, task_id: str, progress: int):
        """Update task progress only"""
        return self.update_task_status(task_id, progress=progress)


# Example usage for external services
if __name__ == "__main__":
    import sys
    
    # Example of correct usage
    updater = TaskUpdater()
    
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        
        # If only timestamp is provided, show error
        if task_id.isdigit():
            print(f"\nError: Invalid task ID format!")
            print(f"You provided: {task_id}")
            print(f"Expected format: task-{task_id}-XXXXXXXXX")
            print(f"\nThe full task ID includes:")
            print(f"  - Prefix: 'task-'")
            print(f"  - Timestamp: {task_id}")
            print(f"  - Hash: 9-character unique identifier")
            print(f"\nExample: task-{task_id}-12a41dbec")
            sys.exit(1)
        
        # Update progress
        print(f"\nUpdating task: {task_id}")
        result = updater.update_progress(task_id, 50)
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print("\nTask Status Updater - Usage Guide")
        print("=" * 50)
        print("\nUsage: python update_task_helper.py <task_id>")
        print("\nExample:")
        print("  python update_task_helper.py task-1754556928-12a41dbec")
        print("\nPython code example:")
        print("  from update_task_helper import TaskUpdater")
        print("  updater = TaskUpdater()")
        print("  updater.mark_processing('task-1754556928-12a41dbec', progress=25)")
        print("  updater.update_progress('task-1754556928-12a41dbec', 50)")
        print("  updater.mark_completed('task-1754556928-12a41dbec', '/results/file.txt')")
        print("\nCommon mistake:")
        print("  ✗ Using only timestamp: '1754556928'")
        print("  ✓ Using full task ID: 'task-1754556928-12a41dbec'")