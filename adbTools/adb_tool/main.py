import tkinter as tk
from tkinterdnd2 import TkinterDnD
import sys
import os

# Add the parent directory to the path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, application_path)

from adb_tool.gui import AdbGui

def main():
    # Fix for PyInstaller: Set TKDND_LIBRARY environment variable and auto_path
    if getattr(sys, 'frozen', False):
        # In PyInstaller bundle
        tkdnd_path = os.path.join(sys._MEIPASS, 'tkdnd')
        
        if os.path.exists(tkdnd_path):
            # Method 1: Set Environment Variable
            os.environ['TKDND_LIBRARY'] = tkdnd_path
            
            # Method 2: Add to Tcl auto_path
            # We need to use forward slashes for Tcl
            tcl_tkdnd_path = tkdnd_path.replace('\\', '/')
            
            # Also add the architecture specific path
            # Assuming Windows x64 for this build environment
            tcl_tkdnd_arch_path = os.path.join(tkdnd_path, 'win-x64').replace('\\', '/')
    
    # Use TkinterDnD.Tk for drag-and-drop support
    root = TkinterDnD.Tk()
    
    # Method 2 continued: Add to auto_path explicitly
    if getattr(sys, 'frozen', False) and os.path.exists(tkdnd_path):
        root.tk.eval(f'lappend auto_path "{tcl_tkdnd_path}"')
        root.tk.eval(f'lappend auto_path "{tcl_tkdnd_arch_path}"')
    
    # Set icon if available, or just title
    # root.iconbitmap('icon.ico') 
    app = AdbGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
