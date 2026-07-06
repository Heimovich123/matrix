import sys
import os
import time
import datetime
import socket
from PIL import Image, ImageDraw

def get_system_info():
    info = []
    info.append(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    info.append(f"Hostname: {socket.gethostname()}")
    
    # Get active processes
    try:
        import subprocess
        # Get first 15 lines of tasklist
        tasklist = subprocess.check_output("tasklist", shell=True, text=True)
        lines = tasklist.splitlines()[:20]
        info.append("\nTop Active Processes:")
        for line in lines[3:]: # skip headers
            if line.strip():
                info.append(f"  {line[:30].strip()}  {line[30:40].strip()}  {line[55:65].strip()}")
    except Exception as e:
        info.append(f"Failed to get processes: {e}")
        
    # Get disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:")
        info.append(f"\nDisk C: space: Free: {free // (2**30)} GB / Total: {total // (2**30)} GB")
    except Exception:
        pass
        
    return "\n".join(info)

def generate_dashboard_image(filepath, error_msg):
    # Create dark-mode premium dashboard (1280x720)
    img = Image.new("RGB", (1280, 720), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((40, 40), "AMN SYSTEM MONITOR - DESKTOP CONTROL", fill=(56, 189, 248)) # Sky 400
    
    # Error / Warning banner
    draw.rectangle([40, 80, 1240, 130], fill=(30, 41, 59)) # Slate 800
    draw.text((60, 95), f"STATUS: ACTIVE (Headless/No Active Display Buffer) | Screen capture failed: {error_msg}", fill=(244, 63, 94)) # Rose 500
    
    # System Info Block
    sys_info = get_system_info()
    draw.text((40, 160), sys_info, fill=(241, 245, 249)) # Slate 100
    
    # Footer
    draw.text((40, 660), r"Antigravity AI Agent Network | C:\Users\User\OneDrive\App\Matrix MCP", fill=(100, 116, 139)) # Slate 500
    
    img.save(filepath)
    print(f"System status dashboard image saved to {filepath}")

def take_screenshot():
    filepath = "desktop_check.png"
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(filepath)
        print("Real screenshot saved successfully using Pillow.")
        return True
    except Exception as e:
        print(f"Pillow screen grab failed: {e}")
        generate_dashboard_image(filepath, str(e))
        return True

if __name__ == "__main__":
    take_screenshot()
    sys.exit(0)
