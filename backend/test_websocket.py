#!/usr/bin/env python3
"""
Test WebSocket functionality for task updates
"""

import asyncio
import websockets
import json
import aiohttp
from datetime import datetime

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/tasks"

async def test_websocket():
    """Test WebSocket connection and task updates"""
    
    print("=" * 50)
    print("WebSocket Test Starting")
    print("=" * 50)
    
    # Step 1: Upload a test file
    print("\n1. Uploading test file...")
    
    async with aiohttp.ClientSession() as session:
        # Create test data
        test_content = "Test novel content for WebSocket testing.\n" * 100
        
        # Create form data
        data = aiohttp.FormData()
        data.add_field('file',
                      test_content.encode('utf-8'),
                      filename='test_websocket.txt',
                      content_type='text/plain')
        
        # Upload file
        async with session.post(f"{API_URL}/api/v1/tasks/upload", data=data) as response:
            upload_result = await response.json()
            task_id = upload_result.get('task_id')
            print(f"File uploaded successfully. Task ID: {task_id}")
    
    # Step 2: Connect to WebSocket
    print("\n2. Connecting to WebSocket...")
    client_id = f"test-client-{datetime.now().timestamp()}"
    ws_uri = f"{WS_URL}/{client_id}"
    
    async with websockets.connect(ws_uri) as websocket:
        print(f"Connected to WebSocket as {client_id}")
        
        # Step 3: Subscribe to task updates
        print(f"\n3. Subscribing to task {task_id}...")
        await websocket.send(json.dumps({
            "type": "subscribe",
            "task_id": task_id
        }))
        
        # Step 4: Listen for updates
        print("\n4. Listening for task updates...")
        print("-" * 30)
        
        # Set a timeout for listening
        timeout = 30  # Listen for 30 seconds
        start_time = asyncio.get_event_loop().time()
        
        try:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Received update:")
                    print(f"  Type: {data.get('type')}")
                    print(f"  Status: {data.get('status')}")
                    print(f"  Progress: {data.get('progress')}%")
                    
                    if data.get('status') == 'completed':
                        print(f"  Result URL: {data.get('result_url')}")
                        print("\nTask completed successfully!")
                        break
                    elif data.get('status') == 'failed':
                        print(f"  Error: {data.get('error_message')}")
                        print("\nTask failed!")
                        break
                        
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await websocket.send(json.dumps({"type": "ping"}))
                    
        except Exception as e:
            print(f"Error during WebSocket communication: {e}")
        
        # Step 5: Unsubscribe
        print(f"\n5. Unsubscribing from task {task_id}...")
        await websocket.send(json.dumps({
            "type": "unsubscribe",
            "task_id": task_id
        }))
        
        print("\n6. Closing WebSocket connection...")
    
    print("\n" + "=" * 50)
    print("WebSocket Test Completed")
    print("=" * 50)

async def simulate_task_processing():
    """Simulate task processing with progress updates"""
    
    print("\n" + "=" * 50)
    print("Simulating Task Processing with WebSocket Updates")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Get the most recent task
        async with session.get(f"{API_URL}/api/v1/tasks/") as response:
            tasks_data = await response.json()
            if not tasks_data['tasks']:
                print("No tasks found. Please upload a file first.")
                return
            
            task = tasks_data['tasks'][0]
            task_id = task['id']
            print(f"\nProcessing task: {task_id}")
            print(f"File: {task['file_name']}")
    
    # Connect to WebSocket to monitor updates
    client_id = f"monitor-{datetime.now().timestamp()}"
    ws_uri = f"{WS_URL}/{client_id}"
    
    async with websockets.connect(ws_uri) as websocket:
        print(f"\nConnected as monitor: {client_id}")
        
        # Subscribe to task
        await websocket.send(json.dumps({
            "type": "subscribe",
            "task_id": task_id
        }))
        
        # Simulate processing with updates
        async with aiohttp.ClientSession() as session:
            # Start processing
            print("\nStarting task processing...")
            update_data = {
                "status": "processing",
                "progress": 0
            }
            async with session.patch(
                f"{API_URL}/api/v1/tasks/{task_id}",
                json=update_data
            ) as response:
                print(f"Status: {response.status}")
            
            # Simulate progress updates
            for progress in [10, 25, 50, 75, 90, 100]:
                await asyncio.sleep(1)  # Simulate processing time
                
                update_data = {"progress": progress}
                if progress == 100:
                    update_data["status"] = "completed"
                    update_data["result_url"] = f"/results/{task_id}.txt"
                
                async with session.patch(
                    f"{API_URL}/api/v1/tasks/{task_id}",
                    json=update_data
                ) as response:
                    print(f"Updated progress to {progress}%")
                
                # Check for WebSocket message
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    data = json.loads(message)
                    print(f"  WebSocket update received: {data.get('type')} - Progress: {data.get('progress')}%")
                except asyncio.TimeoutError:
                    pass
        
        print("\nTask processing simulation completed!")

async def main():
    """Main test function"""
    
    print("WebSocket Test Suite")
    print("=" * 50)
    print("1. Test WebSocket connection and subscription")
    print("2. Simulate task processing with updates")
    print("3. Exit")
    print("=" * 50)
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        await test_websocket()
    elif choice == "2":
        await simulate_task_processing()
    else:
        print("Exiting...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")