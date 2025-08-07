#!/usr/bin/env python3
"""
Test the complete frontend-backend flow with WebSocket updates
"""

import asyncio
import aiohttp
import websockets
import json
from datetime import datetime

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/tasks"
FRONTEND_URL = "http://localhost:5174"

async def test_complete_flow():
    """Test the complete flow: upload -> process -> real-time updates"""
    
    print("=" * 60)
    print("Complete Frontend-Backend Flow Test")
    print("=" * 60)
    print(f"\nAPI Server: {API_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"WebSocket: {WS_URL}")
    print("-" * 60)
    
    # Step 1: Check backend health
    print("\n1. Checking backend health...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/health") as response:
            health = await response.json()
            print(f"   Backend status: {health['status']}")
    
    # Step 2: Upload a test file
    print("\n2. Uploading test file via API...")
    async with aiohttp.ClientSession() as session:
        test_content = """第一章 测试小说
        
这是一个测试文件，用于验证前后端WebSocket实时更新功能。

小说内容：
从前有座山，山里有座庙，庙里有个老和尚在给小和尚讲故事。
讲的什么故事呢？从前有座山...

系统功能测试：
1. 文件上传
2. 任务处理
3. 实时进度更新
4. WebSocket通信

测试内容结束。
""" * 10  # Make it larger for more realistic processing
        
        data = aiohttp.FormData()
        data.add_field('file',
                      test_content.encode('utf-8'),
                      filename='test_novel_flow.txt',
                      content_type='text/plain')
        
        async with session.post(f"{API_URL}/api/v1/tasks/upload", data=data) as response:
            if response.status == 200:
                result = await response.json()
                task_id = result['task_id']
                print(f"   File uploaded successfully!")
                print(f"   Task ID: {task_id}")
                print(f"   File name: {result['file_name']}")
                print(f"   File size: {result['file_size']} bytes")
            else:
                print(f"   Upload failed: {response.status}")
                return
    
    # Step 3: Connect WebSocket and monitor updates
    print("\n3. Connecting to WebSocket for real-time updates...")
    client_id = f"test-flow-{datetime.now().timestamp()}"
    ws_uri = f"{WS_URL}/{client_id}"
    
    async with websockets.connect(ws_uri) as websocket:
        print(f"   Connected as: {client_id}")
        
        # Subscribe to task
        print(f"\n4. Subscribing to task updates...")
        await websocket.send(json.dumps({
            "type": "subscribe",
            "task_id": task_id
        }))
        print(f"   Subscribed to task: {task_id}")
        
        # Monitor updates
        print("\n5. Monitoring real-time progress updates...")
        print("-" * 40)
        
        completed = False
        last_progress = 0
        update_count = 0
        
        while not completed:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(message)
                
                if data.get('type') == 'task_update':
                    update_count += 1
                    current_progress = data.get('progress', 0)
                    status = data.get('status')
                    
                    # Create progress bar
                    bar_length = 30
                    filled = int(bar_length * current_progress / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"   [{datetime.now().strftime('%H:%M:%S')}] "
                          f"[{bar}] {current_progress:3}% - {status}")
                    
                    if status == 'completed':
                        print("-" * 40)
                        print(f"\n✅ Task completed successfully!")
                        print(f"   Result URL: {data.get('result_url')}")
                        print(f"   Total updates received: {update_count}")
                        completed = True
                    elif status == 'failed':
                        print("-" * 40)
                        print(f"\n❌ Task failed!")
                        print(f"   Error: {data.get('error_message')}")
                        completed = True
                    
                    last_progress = current_progress
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                if not completed:
                    await websocket.send(json.dumps({"type": "ping"}))
    
    # Step 6: Verify task status via API
    print("\n6. Verifying final task status via API...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/v1/tasks/{task_id}") as response:
            if response.status == 200:
                task_data = await response.json()
                print(f"   Status: {task_data['status']}")
                print(f"   Progress: {task_data['progress']}%")
                if task_data.get('result_url'):
                    print(f"   Result: {task_data['result_url']}")
    
    # Step 7: Check task statistics
    print("\n7. Checking overall statistics...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/v1/tasks/statistics") as response:
            if response.status == 200:
                stats = await response.json()
                print(f"   Total tasks: {stats['total']}")
                print(f"   Completed: {stats['completed']}")
                print(f"   Processing: {stats['processing']}")
                print(f"   Pending: {stats['pending']}")
                print(f"   Failed: {stats['failed']}")
    
    print("\n" + "=" * 60)
    print("✅ Complete Flow Test Successful!")
    print("=" * 60)

async def monitor_multiple_tasks():
    """Monitor multiple tasks simultaneously"""
    
    print("\n" + "=" * 60)
    print("Multiple Task Monitoring Test")
    print("=" * 60)
    
    task_ids = []
    
    # Upload multiple files
    print("\n1. Uploading 3 test files...")
    async with aiohttp.ClientSession() as session:
        for i in range(3):
            content = f"Test novel {i+1}\n" * 50
            data = aiohttp.FormData()
            data.add_field('file',
                          content.encode('utf-8'),
                          filename=f'test_novel_{i+1}.txt',
                          content_type='text/plain')
            
            async with session.post(f"{API_URL}/api/v1/tasks/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    task_ids.append(result['task_id'])
                    print(f"   Task {i+1}: {result['task_id']}")
    
    # Connect WebSocket and monitor all tasks
    print("\n2. Monitoring all tasks via WebSocket...")
    client_id = f"multi-monitor-{datetime.now().timestamp()}"
    ws_uri = f"{WS_URL}/{client_id}"
    
    async with websockets.connect(ws_uri) as websocket:
        # Subscribe to all tasks
        for task_id in task_ids:
            await websocket.send(json.dumps({
                "type": "subscribe",
                "task_id": task_id
            }))
        
        print("\n3. Receiving real-time updates...")
        print("-" * 40)
        
        task_status = {tid: {'progress': 0, 'status': 'pending'} for tid in task_ids}
        completed_count = 0
        
        while completed_count < len(task_ids):
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(message)
                
                if data.get('type') == 'task_update':
                    task_id = data.get('task_id')
                    if task_id in task_status:
                        task_status[task_id]['progress'] = data.get('progress', 0)
                        task_status[task_id]['status'] = data.get('status')
                        
                        # Display progress for all tasks
                        print(f"\r", end="")
                        for idx, tid in enumerate(task_ids):
                            progress = task_status[tid]['progress']
                            status = task_status[tid]['status']
                            bar_length = 10
                            filled = int(bar_length * progress / 100)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            print(f"Task {idx+1}: [{bar}] {progress:3}% ", end="")
                        
                        if data.get('status') in ['completed', 'failed']:
                            completed_count += 1
                            
            except asyncio.TimeoutError:
                pass
        
        print("\n" + "-" * 40)
        print("\n✅ All tasks completed!")

async def main():
    """Main test menu"""
    
    print("\n" + "=" * 60)
    print("Novel Task Manager - Complete Flow Test Suite")
    print("=" * 60)
    print("\nEnsure both backend and frontend are running:")
    print("  Backend: http://localhost:8000")
    print("  Frontend: http://localhost:5174")
    print("\nTest Options:")
    print("1. Test complete single task flow")
    print("2. Test multiple concurrent tasks")
    print("3. Exit")
    print("-" * 60)
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        await test_complete_flow()
    elif choice == "2":
        await monitor_multiple_tasks()
    else:
        print("Exiting...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")