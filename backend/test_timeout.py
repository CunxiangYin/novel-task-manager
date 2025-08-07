#!/usr/bin/env python3
"""
Test script to verify task timeout functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

async def upload_test_file():
    """Upload a test file to create a task"""
    async with aiohttp.ClientSession() as session:
        # Create test file content
        test_content = "This is a test file for timeout testing.\n" * 100
        
        # Create form data
        form_data = aiohttp.FormData()
        form_data.add_field('file',
                           test_content.encode('utf-8'),
                           filename='timeout_test.txt',
                           content_type='text/plain')
        
        async with session.post(f"{API_BASE_URL}/tasks/upload", data=form_data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ File uploaded successfully")
                print(f"  Task ID: {result['task_id']}")
                return result['task_id']
            else:
                print(f"✗ Upload failed: {response.status}")
                return None

async def monitor_task(task_id, duration_seconds=120):
    """Monitor task status for a specified duration"""
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        last_status = None
        last_progress = -1
        
        print(f"\nMonitoring task {task_id} for {duration_seconds} seconds...")
        print("-" * 50)
        
        while time.time() - start_time < duration_seconds:
            async with session.get(f"{API_BASE_URL}/tasks/{task_id}") as response:
                if response.status == 200:
                    task = await response.json()
                    
                    # Only print when status or progress changes
                    if task['status'] != last_status or task['progress'] != last_progress:
                        elapsed = int(time.time() - start_time)
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        print(f"[{timestamp}] [{elapsed:3d}s] Status: {task['status']:10s} | Progress: {task['progress']:3d}% ", end="")
                        
                        if task['status'] == 'failed' and task.get('error_message'):
                            print(f"\n  ✗ Error: {task['error_message']}")
                        elif task['status'] == 'completed':
                            print(f"\n  ✓ Task completed successfully!")
                        else:
                            print()
                        
                        last_status = task['status']
                        last_progress = task['progress']
                    
                    # Exit if task is completed or failed
                    if task['status'] in ['completed', 'failed']:
                        final_time = int(time.time() - start_time)
                        print("-" * 50)
                        print(f"Task finished after {final_time} seconds with status: {task['status']}")
                        return task
                
            await asyncio.sleep(5)  # Check every 5 seconds
        
        print("-" * 50)
        print(f"Monitoring ended after {duration_seconds} seconds")
        return None

async def test_normal_completion():
    """Test a task that completes normally (simulated quick completion)"""
    print("\n" + "="*60)
    print("TEST 1: Normal Task Completion (Quick Simulation)")
    print("="*60)
    
    # For normal completion test, temporarily reduce timeout in simulation
    # This would complete quickly in the current simulation
    task_id = await upload_test_file()
    if task_id:
        await monitor_task(task_id, duration_seconds=60)

async def test_timeout_scenario():
    """Test a task that should timeout after 30 minutes"""
    print("\n" + "="*60)
    print("TEST 2: Task Timeout Scenario (30-minute timeout)")
    print("="*60)
    print("Note: This test will monitor for 35 minutes to verify timeout at 30 minutes")
    print("You can reduce TASK_TIMEOUT_SECONDS in config.py for faster testing")
    
    task_id = await upload_test_file()
    if task_id:
        # Monitor for 35 minutes (2100 seconds) to see the timeout at 30 minutes
        await monitor_task(task_id, duration_seconds=2100)

async def main():
    """Run timeout tests"""
    print("\n" + "="*60)
    print("TASK TIMEOUT TESTING")
    print("="*60)
    print(f"API URL: {API_BASE_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL.replace('/api/v1', '')}/health") as response:
                if response.status == 200:
                    print("✓ API is running")
                else:
                    print("✗ API is not responding properly")
                    return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("Please ensure the backend is running: python start_local.py")
        return
    
    # Run tests
    print("\nSelect test to run:")
    print("1. Quick test (monitors for 1 minute)")
    print("2. Full timeout test (monitors for 35 minutes)")
    print("3. Upload multiple tasks to test concurrent timeouts")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await test_normal_completion()
    elif choice == "2":
        await test_timeout_scenario()
    elif choice == "3":
        print("\n" + "="*60)
        print("TEST 3: Multiple Concurrent Tasks")
        print("="*60)
        
        # Upload 3 tasks
        task_ids = []
        for i in range(3):
            task_id = await upload_test_file()
            if task_id:
                task_ids.append(task_id)
                print(f"  Task {i+1}: {task_id}")
        
        # Monitor all tasks concurrently
        if task_ids:
            monitor_tasks = [monitor_task(task_id, 60) for task_id in task_ids]
            await asyncio.gather(*monitor_tasks)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())