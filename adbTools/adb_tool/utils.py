import platform
import subprocess
import os
import shlex

def get_platform():
    return platform.system()

def open_terminal(command, title="Terminal"):
    """
    Opens a new terminal window and executes the given command.
    """
    system = get_platform()
    
    if system == "Windows":
        # Windows: Use 'start cmd /k'
        # /k keeps the window open after the command finishes
        cmd = f'start "{title}" cmd /k {command}'
        subprocess.Popen(cmd, shell=True)
        
    elif system == "Darwin":  # macOS
        # macOS: Use AppleScript to tell Terminal to do script
        # We need to escape quotes for AppleScript
        safe_command = command.replace('"', '\\"')
        apple_script = f'''
        tell application "Terminal"
            do script "{safe_command}"
            activate
        end tell
        '''
        subprocess.Popen(['osascript', '-e', apple_script])
        
    else:
        # Linux (Basic support, might need x-terminal-emulator or similar)
        # Trying generic x-terminal-emulator
        try:
            subprocess.Popen(['x-terminal-emulator', '-e', f"bash -c '{command}; exec bash'"])
        except FileNotFoundError:
            print(f"Unsupported platform or terminal emulator not found: {system}")

def run_command_get_output(command):
    """
    Runs a command and returns its output as a string.
    """
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        return ""
