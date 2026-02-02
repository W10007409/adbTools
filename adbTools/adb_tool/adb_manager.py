import os
import sys
import subprocess
from .utils import open_terminal, run_command_get_output

class AdbManager:
    DEVICE_MAP = {
        "5200b937431d4639": "(T583/prod/무한9671)",
        "5200e504ba849645": "(T583/stg/무한6027)",
        "R9TR90HQ6GL": "(T500/stg/무한8721)",
        "WJD06AR03662": "(MPAD1/stg)",
        "WJD09ANF00170": "(MPAD2/stg)"
    }

    def __init__(self):
        self.adb_path = self._get_tool_path("adb")
        self.scrcpy_path = self._get_tool_path("scrcpy")

    def _get_tool_path(self, tool_name):
        """
        Resolves the absolute path to the tool in the 'exec' directory.
        Falls back to system PATH if not found.
        """
        exe_name = f"{tool_name}.exe" if os.name == 'nt' else tool_name
        
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # The 'exec' folder is at the root of the temp directory
            base_dir = sys._MEIPASS
        else:
            # Running as script
            # project_root/adb_tool/adb_manager.py
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        tool_path = os.path.join(base_dir, "exec", exe_name)
        
        if os.path.exists(tool_path):
            return f'"{tool_path}"' # Quote path in case of spaces
            
        return tool_name # Fallback to system PATH

    def get_devices(self):
        """
        Returns a list of tuples (device_id, description).
        """
        output = run_command_get_output(f"{self.adb_path} devices")
        devices = []
        lines = output.splitlines()
        for line in lines[1:]:  # Skip header
            if "\tdevice" in line:
                device_id = line.split("\t")[0]
                description = self.DEVICE_MAP.get(device_id, "(unknown)")
                devices.append((device_id, f"{device_id} {description}"))
        return devices

    def get_installed_packages(self, device_id):
        """
        Returns a list of tuples (package_name, app_name) for installed packages.
        """
        cmd = f"{self.adb_path} -s {device_id} shell pm list packages"
        output = run_command_get_output(cmd)
        packages = []
        
        for line in output.splitlines():
            if line.startswith("package:"):
                package_name = line.replace("package:", "").strip()
                packages.append(package_name)
        
        # Return packages with simple names for now (fast)
        # We'll get real names in the GUI to show progress
        result = []
        for pkg in packages:
            # Use last part of package name as default
            app_name = pkg.split('.')[-1]
            result.append((pkg, app_name))
        
        return sorted(result, key=lambda x: x[1].lower())
    
    def get_app_label(self, device_id, package_name):
        """
        Gets the application label for a specific package.
        Returns the label or None if not found.
        """
        try:
            label_cmd = f"{self.adb_path} -s {device_id} shell pm dump {package_name}"
            label_output = run_command_get_output(label_cmd)
            
            # Look for application label in the output
            for line in label_output.splitlines():
                line = line.strip()
                if "applicationLabel=" in line:
                    # Extract the label
                    app_name = line.split("applicationLabel=", 1)[1].strip()
                    return app_name
        except:
            pass
        
        return None
    
    def get_app_details(self, device_id, package_name):
        """
        Gets detailed information about an app.
        Returns a dictionary with app details.
        """
        details = {
            "package": package_name,
            "name": None,
            "version_name": None,
            "version_code": None,
            "install_date": None,
            "update_date": None,
            "data_dir": None,
            "apk_path": None
        }
        
        try:
            # Get package dump
            dump_cmd = f"{self.adb_path} -s {device_id} shell pm dump {package_name}"
            dump_output = run_command_get_output(dump_cmd)
            
            for line in dump_output.splitlines():
                line = line.strip()
                
                if "applicationLabel=" in line:
                    details["name"] = line.split("applicationLabel=", 1)[1].strip()
                elif "versionName=" in line and not details["version_name"]:
                    details["version_name"] = line.split("versionName=", 1)[1].strip()
                elif "versionCode=" in line and not details["version_code"]:
                    parts = line.split("versionCode=", 1)[1].strip()
                    # Extract just the number
                    details["version_code"] = parts.split()[0] if parts else None
                elif "firstInstallTime=" in line:
                    details["install_date"] = line.split("firstInstallTime=", 1)[1].strip()
                elif "lastUpdateTime=" in line:
                    details["update_date"] = line.split("lastUpdateTime=", 1)[1].strip()
                elif "dataDir=" in line:
                    details["data_dir"] = line.split("dataDir=", 1)[1].strip()
                elif "codePath=" in line and not details["apk_path"]:
                    details["apk_path"] = line.split("codePath=", 1)[1].strip()
            
            # If no name found, use package name
            if not details["name"]:
                details["name"] = package_name.split('.')[-1]
                
        except Exception as e:
            details["name"] = package_name.split('.')[-1]
        
        return details

    def get_device_title(self, device_id):
        """Returns the title for the device window based on ID."""
        if device_id == "5200b937431d4639": return "(T583/prod)"
        if device_id == "5200e504ba849645": return "(T583/stg)"
        if device_id == "R9TR90HQ6GL": return "(T500/stg)"
        if device_id == "WJD06AR03662": return "(MPAD1/stg)"
        if device_id == "WJD09ANF00170": return "(MPAD2/stg)"
        return "(unknown)"

    def execute_action(self, action_id, device_id, **kwargs):
        """
        Executes the specified action on the given device.
        Returns a dict with 'type': 'info'/'action' and 'data': ... if applicable.
        """
        package = kwargs.get("package", "")
        
        if action_id == 0: # Launcher Version
            cmd = f"{self.adb_path} -s {device_id} shell dumpsys package com.wjthinkbig.mlauncher2 | findstr \"versionName versionCode\""
            output = run_command_get_output(cmd)
            return {"type": "info", "data": output, "title": "런쳐 버전 정보"}
            
        elif action_id == 1: # Scrcpy
            title = self.get_device_title(device_id)
            cmd = f"{self.scrcpy_path} -s {device_id} -S --window-title {title} --disable-screensaver --max-size 1024 --always-on-top -t --rotation 0"
            open_terminal(cmd, title="Scrcpy")
            return {"type": "action", "msg": "Scrcpy 실행됨"}

        elif action_id == 2: # Back Button
            cmd = f"{self.adb_path} -s {device_id} shell input keyevent KEYCODE_BACK"
            subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": "뒤로가기 실행됨"}

        elif action_id == 3: # Home Button
            cmd = f"{self.adb_path} -s {device_id} shell input keyevent KEYCODE_HOME"
            subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": "홈 버튼 실행됨"}

        elif action_id == 4: # Screen Off
            cmd = f"{self.adb_path} -s {device_id} shell input keyevent KEYCODE_SLEEP"
            subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": "화면 끄기 실행됨"}

        elif action_id == 5: # Logcat
            if package:
                cmd = f"{self.adb_path} -s {device_id} logcat {package}:* *:s"
            else:
                cmd = f"{self.adb_path} -s {device_id} logcat"
            open_terminal(cmd, title="Logcat")
            return {"type": "action", "msg": "로그캣 실행됨"}

        elif action_id == 55: # Save Log
            save_path = kwargs.get("save_path")
            if not save_path:
                return {"type": "action", "msg": "저장 경로가 지정되지 않았습니다."}
            
            # Use subprocess.run for shell redirection
            cmd = f"{self.adb_path} -s {device_id} logcat -d > \"{save_path}\""
            subprocess.run(cmd, shell=True)
            return {"type": "action", "msg": f"로그 저장 완료: {save_path}"}

        elif action_id == 6: # Battery Info
            cmd = f"{self.adb_path} -s {device_id} shell dumpsys battery"
            output = run_command_get_output(cmd)
            return {"type": "info", "data": output, "title": "배터리 정보"}

        elif action_id == 7: # Adb Shell
            cmd = f"{self.adb_path} -s {device_id} shell"
            open_terminal(cmd, title="ADB Shell")
            return {"type": "action", "msg": "ADB Shell 실행됨"}

        elif action_id == 8: # All Devices Scrcpy
            devices = self.get_devices()
            for dev_id, _ in devices:
                cmd = f"{self.scrcpy_path} -s {dev_id} -S --disable-screensaver --max-size 1024 --always-on-top -t"
                open_terminal(cmd, title=f"Scrcpy {dev_id}")
            return {"type": "action", "msg": "모든 디바이스 Scrcpy 실행됨"}

        elif action_id == 9: # All Devices Sleep
            devices = self.get_devices()
            for dev_id, _ in devices:
                cmd = f"{self.adb_path} -s {dev_id} shell input keyevent KEYCODE_SLEEP"
                subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": "모든 디바이스 화면 끄기 실행됨"}

        elif action_id == 10: # Delete App
            cmd = f"{self.adb_path} -s {device_id} shell am broadcast -n com.wjthinkbig.minstaller2m/com.wjthinkbig.minstaller2.receiver.InstallIfReceiver -a com.wjthinkbig.minstaller2.ACT_APP_DELETE --es APP_PACKAGE_ID {package}"
            subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": f"앱 삭제 완료: {package}"}

        elif action_id == 11: # Install App
            cmd = f"{self.adb_path} -s {device_id} install {package}"
            open_terminal(cmd, title="Install App")
            return {"type": "action", "msg": "앱 설치 명령 실행됨"}

        elif action_id == 12: # Screen Capture Permission
            cmd = f"{self.adb_path} -s {device_id} shell am broadcast -n com.wjthinkbig.mlauncher2/com.wjthinkbig.mlauncher2.broadcast.TopActivityRecevier -a android.intent.action.ACTION_APPLICATION_FOCUS_CHANGE --es application_focus_component_name \"com.rsupport.rs.activity.rsupport.sec\" --es application_focus_status \"gained\""
            subprocess.Popen(cmd, shell=True)
            return {"type": "action", "msg": "화면 캡쳐 권한 부여됨"}

        elif action_id == 13: # Installed App Version
            cmd = f"{self.adb_path} -s {device_id} shell dumpsys package {package} | findstr \"versionName versionCode\""
            output = run_command_get_output(cmd)
            return {"type": "info", "data": output, "title": "앱 버전 정보"}

        elif action_id == 14: # Send Broadcast
            cmd = f"{self.adb_path} -s {device_id} shell am broadcast -a {package}"
            open_terminal(cmd, title="Send Broadcast")
            return {"type": "action", "msg": "브로드캐스트 전송됨"}

        elif action_id == 15: # Top App Info
            cmd = f"{self.adb_path} -s {device_id} shell \"dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'\""
            output = run_command_get_output(cmd)
            return {"type": "info", "data": output, "title": "최상위 앱 정보"}

        elif action_id == 100: # Clear Debug App
            cmd = f"{self.adb_path} -s {device_id} shell \"am clear-debug-app\""
            open_terminal(cmd, title="Clear Debug App")
            return {"type": "action", "msg": "디버그 앱 설정 초기화됨"}
            
        elif action_id == 200: # Screen Capture (New)
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{device_id}_{timestamp}.png"
            
            # 1. Capture to device
            run_command_get_output(f"{self.adb_path} -s {device_id} shell screencap -p /sdcard/temp_screen.png")
            # 2. Pull to local
            run_command_get_output(f"{self.adb_path} -s {device_id} pull /sdcard/temp_screen.png \"{filename}\"")
            # 3. Delete from device
            run_command_get_output(f"{self.adb_path} -s {device_id} shell rm /sdcard/temp_screen.png")
            
            return {"type": "action", "msg": f"캡쳐 완료: {filename}"}

    def list_directories(self, device_id, path):
        """
        Lists directories and files in the given path.
        Returns a list of dicts: {'name': str, 'type': 'dir'|'file'}
        """
        # Ensure path ends with / for proper ls behavior if it's a directory
        if not path.endswith('/'):
            path += '/'
            
        cmd = f"{self.adb_path} -s {device_id} shell ls -F \"{path}\""
        output = run_command_get_output(cmd)
        
        items = []
        for line in output.splitlines():
            line = line.strip()
            if not line: continue
            
            # Simple parsing of 'ls -F' output
            # terminated by / is dir
            # terminated by @ is link
            # others are files (or executables with *)
            
            if line.endswith('/'):
                items.append({'name': line[:-1], 'type': 'dir'})
            elif line.endswith('@'):
                items.append({'name': line[:-1], 'type': 'link'})
            elif line.endswith('*'):
                items.append({'name': line[:-1], 'type': 'file'})
            else:
                items.append({'name': line, 'type': 'file'})
                
        return sorted(items, key=lambda x: (x['type'] != 'dir', x['name']))

    def create_directory(self, device_id, path):
        """Creates a directory on the device."""
        cmd = f"{self.adb_path} -s {device_id} shell mkdir -p \"{path}\""
        run_command_get_output(cmd)
        return True

    def push_file(self, device_id, local_path, remote_path):
        """Pushes a local file to the remote path."""
        # Quote paths to handle spaces
        cmd = f"{self.adb_path} -s {device_id} push \"{local_path}\" \"{remote_path}\""
        output = run_command_get_output(cmd)
        return output
