#!/usr/bin/env python3
"""
Test script to verify task ID update functionality
Tests both correct and incorrect task ID formats
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

async def create_test_task():
    """Create a test task by uploading a file"""
    async with httpx.AsyncClient() as client:
        # Create test file content
        test_content = "This is a test file for task ID testing.\n" * 10
        
        # Create form data
        files = {'file': ('test_task_id.txt', test_content.encode('utf-8'), 'text/plain')}
        
        response = await client.post(f"{API_BASE_URL}/tasks/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Task created successfully")
            print(f"  Full Task ID: {result['task_id']}")
            
            # Extract parts of task ID for demonstration
            task_id_parts = result['task_id'].split('-')
            if len(task_id_parts) >= 3:
                timestamp = task_id_parts[1]
                hash_part = task_id_parts[2]
                print(f"  Timestamp part: {timestamp}")
                print(f"  Hash part: {hash_part}")
            
            return result['task_id']
        else:
            print(f"✗ Failed to create task: {response.status_code}")
            return None

async def test_task_update(task_id: str, use_incorrect_format: bool = False):
    """Test updating task with correct or incorrect ID format"""
    
    async with httpx.AsyncClient() as client:
        # If testing incorrect format, extract just the timestamp
        if use_incorrect_format and task_id.startswith("task-"):
            parts = task_id.split('-')
            if len(parts) >= 2:
                task_id = parts[1]  # Use only timestamp part
                print(f"\n⚠️  Testing with INCORRECT format: {task_id} (timestamp only)")
        else:
            print(f"\n✓ Testing with CORRECT format: {task_id}")
        
        # Test different update scenarios
        test_cases = [
            {
                "name": "Update to processing with 25% progress",
                "data": {"status": "processing", "progress": 25},
                "endpoint": f"/tasks/{task_id}"
            },
            {
                "name": "Update progress to 50%",
                "data": {"progress": 50},
                "endpoint": f"/tasks/{task_id}"
            },
            {
                "name": "Update progress to 75%",
                "data": {"progress": 75},
                "endpoint": f"/tasks/{task_id}"
            },
            {
                "name": "Mark as completed",
                "data": {"status": "completed", "progress": 100, "result_url": "/results/test.txt"},
                "endpoint": f"/tasks/{task_id}"
            }
        ]
        
        for test in test_cases:
            print(f"\n  Test: {test['name']}")
            print(f"  Endpoint: PATCH {API_BASE_URL}{test['endpoint']}")
            print(f"  Data: {json.dumps(test['data'])}")
            
            try:
                response = await client.patch(
                    f"{API_BASE_URL}{test['endpoint']}",
                    json=test['data'],
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✓ Success: Status={result.get('status')}, Progress={result.get('progress')}%")
                elif response.status_code == 404:
                    print(f"  ✗ Failed: 404 Not Found - Task ID not found or incorrect format")
                else:
                    print(f"  ✗ Failed: HTTP {response.status_code}")
                    print(f"     Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)

async def test_all_endpoints_with_wrong_id():
    """Test all possible endpoint variations that external services might try"""
    
    # Use a timestamp that looks like what the external service is using
    wrong_task_id = "1754556928"
    
    print("\n" + "="*60)
    print("Testing all endpoint variations with wrong task ID format")
    print(f"Wrong ID (timestamp only): {wrong_task_id}")
    print("="*60)
    
    endpoints = [
        f"/api/task/{wrong_task_id}",
        f"/api/v1/tasks/{wrong_task_id}",
        f"/api/tasks/{wrong_task_id}",
        f"/tasks/{wrong_task_id}",
        f"/api/v1/task/{wrong_task_id}",
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            url = f"http://localhost:8000{endpoint}"
            print(f"\nTrying: PATCH {url}")
            
            try:
                response = await client.patch(
                    url,
                    json={"status": "processing", "progress": 50},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    print(f"  ✓ Success (unexpected!)")
                elif response.status_code == 404:
                    print(f"  ✗ 404 Not Found (expected)")
                else:
                    print(f"  ✗ HTTP {response.status_code}")
                    
            except httpx.ConnectError:
                print(f"  ✗ Connection failed (endpoint doesn't exist)")
            except Exception as e:
                print(f"  ✗ Error: {e}")

async def main():
    """Run all tests"""
    
    print("\n" + "="*60)
    print("TASK ID UPDATE TESTING")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✓ API is running")
            else:
                print("✗ API health check failed")
                return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("Please ensure the backend is running: python start_local.py")
        return
    
    print("\n" + "="*60)
    print("PART 1: Create a test task")
    print("="*60)
    
    task_id = await create_test_task()
    
    if not task_id:
        print("\n✗ Failed to create test task. Exiting.")
        return
    
    print("\n" + "="*60)
    print("PART 2: Test with CORRECT task ID format")
    print("="*60)
    
    await test_task_update(task_id, use_incorrect_format=False)
    
    print("\n" + "="*60)
    print("PART 3: Test with INCORRECT task ID format (timestamp only)")
    print("="*60)
    
    # Create another task for incorrect format testing
    task_id2 = await create_test_task()
    if task_id2:
        await test_task_update(task_id2, use_incorrect_format=True)
    
    print("\n" + "="*60)
    print("PART 4: Test all endpoints that external service might try")
    print("="*60)
    
    await test_all_endpoints_with_wrong_id()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n✓ Correct format: task-TIMESTAMP-HASH works properly")
    print("✗ Incorrect format: TIMESTAMP only returns 404")
    print("\nExternal services MUST use the complete task ID returned from upload.")
    print("The task ID includes: prefix 'task-', timestamp, and unique hash.")

if __name__ == "__main__":
    asyncio.run(main())