#!/usr/bin/env python3
"""
Quick timeout test with reduced timeout for faster testing
To use this, temporarily change TASK_TIMEOUT_SECONDS in config.py to 60 (1 minute)
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_quick_timeout():
    """Test timeout with 1-minute limit"""
    
    # First, modify the task processor to simulate a longer task
    print("Quick Timeout Test")
    print("=" * 50)
    print("Prerequisites:")
    print("1. Set TASK_TIMEOUT_SECONDS = 60 in app/config.py")
    print("2. Modify simulate_processing to use update_interval = 5")
    print("3. Start the backend: python start_local.py")
    print("=" * 50)
    
    input("\nPress Enter when ready to start test...")
    
    # Import the test module and run
    from test_timeout import upload_test_file, monitor_task
    
    print("\nUploading test file...")
    task_id = await upload_test_file()
    
    if task_id:
        print(f"\nMonitoring task {task_id} (should timeout after 60 seconds)...")
        result = await monitor_task(task_id, duration_seconds=90)
        
        if result and result['status'] == 'failed':
            if 'timeout' in result.get('error_message', '').lower():
                print("\n✓ SUCCESS: Task correctly timed out!")
            else:
                print("\n✗ FAILED: Task failed but not due to timeout")
                print(f"  Error: {result.get('error_message')}")
        elif result and result['status'] == 'completed':
            print("\n✗ FAILED: Task completed instead of timing out")
        else:
            print("\n⚠ Test inconclusive")
    else:
        print("\n✗ Failed to upload test file")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("QUICK TIMEOUT TEST (1-minute timeout)")
    print("="*60)
    
    asyncio.run(test_quick_timeout())