# ADB GUI Tool Implementation Plan

## Goal
Convert an existing Windows Batch script for ADB device management into a cross-platform (Windows/macOS) Python GUI application.

## User Review Required
- **Dependencies**: The app requires `adb` and `scrcpy` to be installed and available in the system PATH.
- **Platform Behavior**: 
    - On Windows, `start cmd /k` is used to open new terminal windows.
    - On macOS, `osascript` (AppleScript) will be used to open Terminal.app and execute commands.

## Proposed Changes

### Project Structure
The application will be structured as a Python package in `adb_tool/`.

#### [NEW] [utils.py](file:///C:/Users/10007409/.gemini/antigravity/brain/ad0e81c3-09d3-4157-bb48-659d92c5bf59/adb_tool/utils.py)
- `open_terminal(command)`: Function to open a new terminal window and run a command, handling OS differences.
- `get_platform()`: Helper to identify the OS.

#### [NEW] [adb_manager.py](file:///C:/Users/10007409/.gemini/antigravity/brain/ad0e81c3-09d3-4157-bb48-659d92c5bf59/adb_tool/adb_manager.py)
- `DEVICE_MAP`: Dictionary mapping device IDs to friendly names.
- `AdbManager` class:
    - `get_devices()`: Parses `adb devices` output.
    - `execute_action(action_id, device_id, **kwargs)`: Handles the logic for each menu item.
    - Methods for specific complex commands (broadcasts, etc.).

#### [NEW] [gui.py](file:///C:/Users/10007409/.gemini/antigravity/brain/ad0e81c3-09d3-4157-bb48-659d92c5bf59/adb_tool/gui.py)
- `AdbGui` class:
    - Main Tkinter window.
    - Device selection dropdown (Combobox).
    - Input fields for dynamic parameters (Package, Tag, etc.).
    - Grid/List of buttons corresponding to the batch script actions.
    - Output log area for non-terminal commands.

#### [NEW] [main.py](file:///C:/Users/10007409/.gemini/antigravity/brain/ad0e81c3-09d3-4157-bb48-659d92c5bf59/adb_tool/main.py)
- Entry point to launch the application.

## Verification Plan
### Automated Tests
- None (GUI app).

### Manual Verification
- Run `python adb_tool/main.py`.
- Verify device list populates correctly.
- Test "Check Launcher Version" (Action 0) - should show output in GUI or terminal.
- Test "Scrcpy" (Action 1) - should launch scrcpy.
- Test "Logcat" (Action 5) - should open a new terminal window.
