#!/usr/bin/env python3
"""
Setup script to configure the application for LAN access
Updates frontend configuration to use the LAN IP
"""

import socket
import json
import os
from pathlib import Path

def get_lan_ip():
    """Get the LAN IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def update_frontend_config(lan_ip):
    """Update frontend configuration to use LAN IP"""
    frontend_config_path = Path(__file__).parent.parent / "frontend" / "src" / "config" / "index.ts"
    
    if frontend_config_path.exists():
        print(f"Updating frontend config at: {frontend_config_path}")
        
        # Read current config
        with open(frontend_config_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = frontend_config_path.with_suffix('.ts.backup')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"Created backup at: {backup_path}")
        
        # Update API URLs
        new_content = content
        new_content = new_content.replace(
            "API_URL: 'http://localhost:8000/api/v1'",
            f"API_URL: 'http://{lan_ip}:8000/api/v1'"
        )
        new_content = new_content.replace(
            "WS_URL: 'ws://localhost:8000/api/v1/ws'",
            f"WS_URL: 'ws://{lan_ip}:8000/api/v1/ws'"
        )
        
        # Write updated config
        with open(frontend_config_path, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Frontend config updated to use: http://{lan_ip}:8000")
        return True
    else:
        print(f"✗ Frontend config not found at: {frontend_config_path}")
        return False

def print_instructions(lan_ip):
    """Print setup instructions"""
    print("\n" + "="*60)
    print("LAN ACCESS SETUP COMPLETE")
    print("="*60)
    
    print(f"\n📡 Your LAN IP: {lan_ip}")
    
    print("\n📦 Backend Setup:")
    print("1. Start the backend with LAN access:")
    print("   cd backend")
    print("   python start_lan.py")
    
    print("\n💻 Frontend Setup:")
    print("1. Start the frontend development server:")
    print("   cd frontend")
    print("   npm run dev -- --host")
    print("\n   OR with specific host:")
    print(f"   npm run dev -- --host {lan_ip}")
    
    print("\n📱 Access from other devices:")
    print(f"1. Backend API: http://{lan_ip}:8000")
    print(f"2. Frontend: http://{lan_ip}:5174")
    print(f"3. API Docs: http://{lan_ip}:8000/docs")
    
    print("\n⚠️  Security Notes:")
    print("• Only use this for local development/testing")
    print("• Your firewall may block incoming connections")
    print("• On macOS, you may need to allow incoming connections")
    print("• On Windows, check Windows Defender Firewall settings")
    
    print("\n🔧 Troubleshooting:")
    print("• Ensure devices are on the same network")
    print("• Check firewall settings on the host machine")
    print("• Try accessing from the host first: http://localhost:8000")
    print(f"• Verify the IP is correct: ping {lan_ip}")
    
    print("\n🔄 To restore localhost-only access:")
    print("1. Restore frontend config from backup:")
    print("   cp frontend/src/config/index.ts.backup frontend/src/config/index.ts")
    print("2. Use start_local.py instead of start_lan.py")
    
    print("="*60)

def main():
    print("\n" + "="*60)
    print("SETTING UP LAN ACCESS")
    print("="*60)
    
    # Get LAN IP
    lan_ip = get_lan_ip()
    
    if not lan_ip:
        print("✗ Could not detect LAN IP address")
        print("  Please check your network connection")
        return
    
    print(f"\n✓ Detected LAN IP: {lan_ip}")
    
    # Ask for confirmation
    response = input(f"\nConfigure frontend to use {lan_ip}? (y/n): ").strip().lower()
    
    if response == 'y':
        if update_frontend_config(lan_ip):
            print_instructions(lan_ip)
        else:
            print("\n✗ Failed to update frontend config")
            print("  Please update manually in frontend/src/config/index.ts")
    else:
        print("\nSetup cancelled. No changes made.")
        print_instructions(lan_ip)

if __name__ == "__main__":
    main()