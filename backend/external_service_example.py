#!/usr/bin/env python3
"""
Example of how external services should integrate with the Task Manager API
This demonstrates the correct way to handle task IDs and update task status
"""

import httpx
import asyncio
import json
from typing import Optional, Dict, Any

class NovelTaskManagerClient:
    """Client for interacting with Novel Task Manager API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        
    async def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file and get the task ID
        
        Returns:
            Full task ID (e.g., "task-1754556928-12a41dbec") or None if failed
        """
        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'text/plain')}
                response = await client.post(
                    f"{self.base_url}{self.api_prefix}/tasks/upload",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data['task_id']
                print(f"✓ File uploaded successfully")
                print(f"  Task ID: {task_id}")
                
                # IMPORTANT: Store the COMPLETE task ID
                # Don't try to parse or extract parts of it
                return task_id
            else:
                print(f"✗ Upload failed: {response.status_code}")
                return None
    
    async def update_task_status(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        result_url: Optional[str] = None
    ) -> bool:
        """
        Update task status using the COMPLETE task ID
        
        Args:
            task_id: MUST be the complete ID (e.g., "task-1754556928-12a41dbec")
                    NOT just the timestamp (e.g., "1754556928")
        
        Returns:
            True if successful, False otherwise
        """
        
        # Validate that we have a complete task ID
        if not task_id.startswith("task-"):
            print(f"❌ ERROR: Invalid task ID format: {task_id}")
            print(f"   Expected format: task-TIMESTAMP-HASH")
            print(f"   Example: task-1754556928-12a41dbec")
            return False
        
        # Build update payload
        update_data = {}
        if status:
            update_data["status"] = status
        if progress is not None:
            update_data["progress"] = progress
        if error_message:
            update_data["error_message"] = error_message
        if result_url:
            update_data["result_url"] = result_url
        
        # Make the API call with COMPLETE task ID
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(url, json=update_data)
                
                if response.status_code == 200:
                    print(f"✓ Task {task_id} updated successfully")
                    return True
                elif response.status_code == 404:
                    print(f"✗ Task not found: {task_id}")
                    print(f"  Make sure you're using the complete task ID")
                    return False
                else:
                    print(f"✗ Update failed: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"✗ Error updating task: {e}")
                return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        
        if not task_id.startswith("task-"):
            print(f"❌ ERROR: Invalid task ID format: {task_id}")
            return None
        
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"✗ Failed to get task status: HTTP {response.status_code}")
                    return None
            except Exception as e:
                print(f"✗ Error getting task status: {e}")
                return None


class ExternalNovelProcessor:
    """
    Example external service that processes novels
    This shows the CORRECT way to integrate with the Task Manager API
    """
    
    def __init__(self):
        self.client = NovelTaskManagerClient()
        self.task_registry = {}  # Store task IDs for our processing
    
    async def process_novel(self, file_path: str):
        """
        Complete workflow for processing a novel
        """
        print(f"\n{'='*60}")
        print(f"Processing novel: {file_path}")
        print(f"{'='*60}")
        
        # Step 1: Upload file and get task ID
        task_id = await self.client.upload_file(file_path)
        
        if not task_id:
            print("Failed to create task")
            return
        
        # IMPORTANT: Store the COMPLETE task ID
        # Never try to extract just the timestamp
        self.task_registry[file_path] = task_id
        
        # Step 2: Mark as processing
        await self.client.update_task_status(
            task_id,  # Use COMPLETE task ID
            status="processing",
            progress=0
        )
        
        # Step 3: Simulate processing with progress updates
        for progress in [10, 25, 50, 75, 90]:
            await asyncio.sleep(1)  # Simulate work
            
            # Always use the COMPLETE task ID
            await self.client.update_task_status(
                task_id,  # Use COMPLETE task ID
                progress=progress
            )
            
            print(f"  Processing... {progress}%")
        
        # Step 4: Mark as completed
        result_path = f"/results/{task_id}.txt"
        await self.client.update_task_status(
            task_id,  # Use COMPLETE task ID
            status="completed",
            progress=100,
            result_url=result_path
        )
        
        print(f"✓ Novel processing completed!")
        print(f"  Task ID: {task_id}")
        print(f"  Result: {result_path}")
        
        # Step 5: Verify final status
        final_status = await self.client.get_task_status(task_id)
        if final_status:
            print(f"\nFinal task status:")
            print(f"  Status: {final_status.get('status')}")
            print(f"  Progress: {final_status.get('progress')}%")
            print(f"  Result URL: {final_status.get('result_url')}")


# Example of INCORRECT implementation (what NOT to do)
class IncorrectExternalService:
    """
    This shows COMMON MISTAKES that cause 404 errors
    """
    
    async def wrong_way_to_update(self):
        """Examples of what NOT to do"""
        
        print("\n" + "="*60)
        print("COMMON MISTAKES (What NOT to do)")
        print("="*60)
        
        # ❌ WRONG: Using only timestamp
        timestamp = "1754556928"
        url = f"http://localhost:8000/api/v1/tasks/{timestamp}"
        print(f"\n❌ WRONG: Using only timestamp")
        print(f"   URL: PATCH {url}")
        print(f"   Result: 404 Not Found")
        
        # ❌ WRONG: Trying to construct task ID manually
        manual_id = f"task-{timestamp}"  # Missing hash part!
        url = f"http://localhost:8000/api/v1/tasks/{manual_id}"
        print(f"\n❌ WRONG: Manually constructing incomplete ID")
        print(f"   URL: PATCH {url}")
        print(f"   Result: 404 Not Found")
        
        # ❌ WRONG: Parsing task ID and losing parts
        full_task_id = "task-1754556928-12a41dbec"
        parts = full_task_id.split('-')
        timestamp_only = parts[1]  # Losing the hash part!
        url = f"http://localhost:8000/api/v1/tasks/{timestamp_only}"
        print(f"\n❌ WRONG: Extracting timestamp from full ID")
        print(f"   Original ID: {full_task_id}")
        print(f"   Used: {timestamp_only}")
        print(f"   URL: PATCH {url}")
        print(f"   Result: 404 Not Found")
        
        # ✅ CORRECT: Using complete task ID
        url = f"http://localhost:8000/api/v1/tasks/{full_task_id}"
        print(f"\n✅ CORRECT: Using complete task ID")
        print(f"   URL: PATCH {url}")
        print(f"   Result: 200 OK")


async def main():
    """Run examples"""
    
    print("\n" + "="*60)
    print("NOVEL TASK MANAGER - EXTERNAL SERVICE INTEGRATION GUIDE")
    print("="*60)
    
    # Show correct implementation
    processor = ExternalNovelProcessor()
    
    # Create a test file
    test_file = "test_novel.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test novel content.\n" * 100)
    
    # Process the novel correctly
    await processor.process_novel(test_file)
    
    # Show common mistakes
    incorrect_service = IncorrectExternalService()
    await incorrect_service.wrong_way_to_update()
    
    print("\n" + "="*60)
    print("KEY TAKEAWAYS")
    print("="*60)
    print("\n1. ALWAYS use the complete task ID returned from upload")
    print("2. NEVER extract or parse parts of the task ID")
    print("3. Store task IDs as-is in your database/registry")
    print("4. The task ID format is: task-TIMESTAMP-HASH")
    print("5. All three parts are required for API calls")


if __name__ == "__main__":
    # Check if API is running
    import httpx
    try:
        with httpx.Client() as client:
            response = client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ API is running")
                asyncio.run(main())
            else:
                print("✗ API health check failed")
    except Exception as e:
        print(f"✗ API is not running: {e}")
        print("Please start it with: python start_local.py")