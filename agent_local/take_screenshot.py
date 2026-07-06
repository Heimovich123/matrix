import sys
import os
import ctypes
from PIL import ImageGrab

# Win32 Constants
WINSTA_ALL_ACCESS = 0x37F
DESKTOP_ALL_ACCESS = 0x1FF

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def switch_to_interactive_desktop():
    try:
        # Open Window Station WinSta0
        hwinsta = user32.OpenWindowStationW("WinSta0", False, WINSTA_ALL_ACCESS)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
            
        # Open Desktop Default
        hdesk = user32.OpenDesktopW("Default", 0, False, DESKTOP_ALL_ACCESS)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
        print("Successfully switched to interactive window station and desktop.")
    except Exception as e:
        print(f"Failed to switch window station/desktop: {e}")

def take_screenshot():
    filepath = "desktop_check.png"
    
    # Switch to interactive desktop session to bypass Windows GUI isolation
    switch_to_interactive_desktop()
    
    try:
        print("Capturing screen using Pillow ImageGrab...")
        img = ImageGrab.grab()
        img.save(filepath)
        print(f"Screenshot saved successfully to {filepath}")
        return True
    except Exception as e:
        print(f"Pillow screen grab failed: {e}")
        return False

if __name__ == "__main__":
    if take_screenshot():
        sys.exit(0)
    else:
        sys.exit(1)
