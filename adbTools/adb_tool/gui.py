import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .adb_manager import AdbManager
import threading
import os

class AdbGui:
    def __init__(self, root):
        self.root = root
        self.root.title("WJ Pad Controller - 웅진북클럽 패드 관리 도구")
        self.root.geometry("600x900")

        # Use a modern, clean dark theme
        self.style = ttk.Style(theme="cyborg")

        self.manager = AdbManager()
        self.selected_device_id = None

        # Store button references for showing/hiding
        self.device_buttons = []
        self.action_frames = []

        self.create_widgets()
        self.refresh_devices()

    def create_widgets(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=BOTH, expand=YES)

        # Header with Help Button
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, text="WJ Pad Controller", font=("Helvetica", 20, "bold"), bootstyle="inverse-dark")
        header_label.pack(side=LEFT)
        
        help_btn = ttk.Button(header_frame, text="❓ 도움말", command=self.show_help, bootstyle="outline-info", width=10)
        help_btn.pack(side=RIGHT)

        # Device Selection Section
        device_frame = ttk.Labelframe(main_container, text="디바이스 선택", padding="15", bootstyle="secondary")
        device_frame.pack(fill=X, pady=10)
        
        self.device_combo = ttk.Combobox(device_frame, state="readonly", bootstyle="secondary")
        self.device_combo.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_select)
        
        refresh_btn = ttk.Button(device_frame, text="새로고침", command=self.refresh_devices, bootstyle="outline-secondary")
        refresh_btn.pack(side=RIGHT)

        # Input Section
        input_frame = ttk.Labelframe(main_container, text="파라미터 (패키지 / 태그 / 액션)", padding="15", bootstyle="secondary")
        input_frame.pack(fill=X, pady=10)
        
        self.param_var = tk.StringVar()
        self.param_entry = ttk.Entry(input_frame, textvariable=self.param_var, bootstyle="secondary")
        self.param_entry.pack(fill=X)

        # Actions Section
        action_frame = ttk.Labelframe(main_container, text="기능 실행", padding="15", bootstyle="secondary")
        action_frame.pack(fill=BOTH, expand=YES, pady=10)
        self.action_frames.append(action_frame)

        # Device Control Section
        device_control_label = ttk.Label(action_frame, text="🖥️ 디바이스 제어", font=("Helvetica", 11, "bold"), bootstyle="primary")
        device_control_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        device_actions = [
            (1, "화면 미러링", "primary"),
            (2, "뒤로가기", "primary"),
            (3, "홈 버튼", "primary"),
            (4, "화면 끄기", "primary"),
            (200, "화면 캡쳐", "primary"),
            (201, "파일 복사", "success"),
            (12, "캡쳐 권한 부여", "primary"),
        ]

        row_offset = 1
        for i, (action_id, label, style) in enumerate(device_actions):
            btn = ttk.Button(action_frame, text=label,
                             command=lambda aid=action_id: self.run_action(aid),
                             bootstyle=style, width=20)
            btn.grid(row=row_offset + i//3, column=i%3, sticky="ew", padx=5, pady=5)
            self.device_buttons.append(btn)
        
        # App Management Section
        row_offset += (len(device_actions) + 2) // 3 + 1
        app_mgmt_label = ttk.Label(action_frame, text="📱 앱 관리", font=("Helvetica", 11, "bold"), bootstyle="success")
        app_mgmt_label.grid(row=row_offset, column=0, columnspan=3, sticky="w", pady=(15, 10))
        row_offset += 1

        app_actions = [
            (11, "앱 설치", "success"),
            (10, "앱 삭제", "success"),
        ]

        for i, (action_id, label, style) in enumerate(app_actions):
            btn = ttk.Button(action_frame, text=label,
                             command=lambda aid=action_id: self.run_action(aid),
                             bootstyle=style, width=20)
            btn.grid(row=row_offset + i//3, column=i%3, sticky="ew", padx=5, pady=5)
            self.device_buttons.append(btn)
        
        # Information & Debug Section
        row_offset += (len(app_actions) + 2) // 3 + 1
        info_label = ttk.Label(action_frame, text="🔧 정보 및 디버깅", font=("Helvetica", 11, "bold"), bootstyle="info")
        info_label.grid(row=row_offset, column=0, columnspan=3, sticky="w", pady=(15, 10))
        row_offset += 1

        info_actions = [
            (0, "런처 버전", "info"),
            (6, "배터리 정보", "info"),
            (15, "최상위 앱", "info"),
            (5, "로그캣 실행", "info"),
            (55, "로그 저장", "success"),
            (14, "브로드캐스트", "info"),
        ]

        for i, (action_id, label, style) in enumerate(info_actions):
            btn = ttk.Button(action_frame, text=label,
                             command=lambda aid=action_id: self.run_action(aid),
                             bootstyle=style, width=20)
            btn.grid(row=row_offset + i//3, column=i%3, sticky="ew", padx=5, pady=5)
            self.device_buttons.append(btn)

        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)

        # Global Actions Section
        global_frame = ttk.Labelframe(main_container, text="전체 디바이스 제어", padding="15", bootstyle="secondary")
        global_frame.pack(fill=X, pady=10)
        
        ttk.Button(global_frame, text="모든 디바이스 화면 띄우기", 
                   command=lambda: self.run_action(8), bootstyle="outline-primary").pack(side=LEFT, expand=YES, fill=X, padx=5, pady=5)
        ttk.Button(global_frame, text="모든 디바이스 화면 끄기", 
                   command=lambda: self.run_action(9), bootstyle="outline-secondary").pack(side=LEFT, expand=YES, fill=X, padx=5, pady=5)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("준비 완료")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", bootstyle="inverse-secondary", padding=5)
        status_bar.pack(side=BOTTOM, fill=X)

    def refresh_devices(self):
        devices = self.manager.get_devices()
        if not devices:
            self.device_combo['values'] = ["디바이스 없음"]
            self.device_combo.current(0)
            self.selected_device_id = None
            self.update_button_visibility(False)
            # Show help if no devices
            self.root.after(100, self.show_help)
        else:
            self.current_devices = devices
            display_values = [desc for _, desc in devices]
            self.device_combo['values'] = display_values
            if display_values:
                self.device_combo.current(0)
                self.selected_device_id = devices[0][0]
                self.update_button_visibility(True)

    def on_device_select(self, event):
        idx = self.device_combo.current()
        if hasattr(self, 'current_devices') and idx < len(self.current_devices):
            self.selected_device_id = self.current_devices[idx][0]
            self.update_button_visibility(True)
        else:
            self.selected_device_id = None
            self.update_button_visibility(False)

    def update_button_visibility(self, is_connected):
        """
        Show or hide device-dependent buttons based on connection status.
        """
        for btn in self.device_buttons:
            if is_connected:
                btn.grid()  # Show button
            else:
                btn.grid_remove()  # Hide button but keep grid space

        for frame in self.action_frames:
            if is_connected:
                frame.pack(fill=BOTH, expand=YES, pady=10)
            else:
                frame.pack_forget()  # Completely hide frame

    def run_action(self, action_id):
        if action_id not in [8, 9] and not self.selected_device_id:
            messagebox.showwarning("경고", "디바이스를 먼저 선택해주세요.")
            return

        # Special handling for Install App (11)
        if action_id == 11:
            self.open_install_popup()
            return
        
        # Special handling for Delete App (10)
        if action_id == 10:
            self.open_delete_popup()
            return

        # Special handling for File Push (201)
        if action_id == 201:
            self.open_file_push_popup()
            return

        # Special handling for Save Log (55)
        if action_id == 55:
            from tkinter import filedialog
            import datetime
            
            default_name = f"logcat_{self.selected_device_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_name,
                title="로그 저장 위치 선택"
            )
            
            if not save_path:
                return

            self.status_var.set("로그 저장 중...")
            
            def task():
                try:
                    result = self.manager.execute_action(action_id, self.selected_device_id, save_path=save_path)
                    self.root.after(0, lambda: self.handle_result(result))
                except Exception as e:
                    self.root.after(0, lambda: self.handle_error(str(e)))
            
            threading.Thread(target=task).start()
            return

        param = self.param_var.get()
        
        if action_id in [14] and not param:
            messagebox.showwarning("경고", "이 기능은 파라미터(패키지명 등)가 필요합니다.")
            self.param_entry.focus()
            return

        self.status_var.set(f"실행 중: 기능 {action_id}...")
        
        def task():
            try:
                result = self.manager.execute_action(action_id, self.selected_device_id, package=param)
                
                # Handle result on main thread
                self.root.after(0, lambda: self.handle_result(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_error(str(e)))

        threading.Thread(target=task).start()

    def open_install_popup(self):
        """
        Opens a popup window for Drag-and-Drop APK installation with modern design.
        """
        popup = tk.Toplevel(self.root)
        popup.title("APK 설치")
        popup.geometry("500x400")
        popup.configure(bg="#1a1a2e")
        
        # Main container
        container = ttk.Frame(popup, padding="30")
        container.pack(fill=BOTH, expand=YES)
        
        # Title
        title_label = ttk.Label(
            container, 
            text="📦 APK 파일 설치", 
            font=("Helvetica", 18, "bold"), 
            bootstyle="inverse-primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Drop zone frame with border
        drop_frame = ttk.Frame(container, bootstyle="primary")
        drop_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Inner drop zone
        drop_zone = ttk.Label(
            drop_frame,
            text="⬇️\n\nAPK 파일을 여기에\n드래그하세요\n\n또는 클릭하여 선택",
            font=("Helvetica", 14),
            bootstyle="inverse-primary",
            anchor="center",
            justify="center"
        )
        drop_zone.pack(fill=BOTH, expand=YES, padx=3, pady=3)
        
        # Info text
        info_label = ttk.Label(
            container,
            text="지원 형식: .apk",
            font=("Helvetica", 9),
            bootstyle="secondary"
        )
        info_label.pack(pady=(10, 0))
        
        # Hover effect simulation
        def on_enter(e):
            drop_zone.configure(bootstyle="inverse-success")
            drop_frame.configure(bootstyle="success")
        
        def on_leave(e):
            drop_zone.configure(bootstyle="inverse-primary")
            drop_frame.configure(bootstyle="primary")
        
        drop_zone.bind("<Enter>", on_enter)
        drop_zone.bind("<Leave>", on_leave)
        
        # File dialog on click
        def on_click(e):
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="APK 파일 선택",
                filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
            )
            if file_path:
                install_apk(file_path)
        
        drop_zone.bind("<Button-1>", on_click)
        
        # Register drop target
        def install_apk(file_path):
            # Handle curly braces if path has spaces (TkinterDnD quirk)
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]
                
            if not file_path.lower().endswith(".apk"):
                messagebox.showerror("에러", "APK 파일만 지원합니다.")
                return
                
            popup.destroy()
            self.status_var.set(f"설치 중: {file_path}")
            
            def task():
                try:
                    result = self.manager.execute_action(11, self.selected_device_id, package=file_path)
                    self.root.after(0, lambda: self.handle_result(result))
                except Exception as e:
                    self.root.after(0, lambda: self.handle_error(str(e)))
                    
            threading.Thread(target=task).start()
        
        try:
            popup.drop_target_register("DND_Files")
            popup.dnd_bind("<<Drop>>", lambda e: install_apk(e.data))
        except Exception as e:
            info_label.config(text=f"Drag & Drop 비활성화됨. 클릭하여 파일을 선택하세요.")
        
        # Close button
        close_btn = ttk.Button(
            container,
            text="취소",
            command=popup.destroy,
            bootstyle="secondary",
            width=15
        )
        close_btn.pack(pady=(20, 0))

    def open_file_push_popup(self):
        """
        Opens a popup window for File Push with Drag-and-Drop and folder navigation.
        """
        popup = tk.Toplevel(self.root)
        popup.title("파일 복사")
        popup.geometry("600x700")
        
        # Main container
        container = ttk.Frame(popup, padding="20")
        container.pack(fill=BOTH, expand=YES)
        
        # Title
        title_label = ttk.Label(
            container, 
            text="📂 파일 복사 (PC -> Device)", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="inverse-primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Variables
        self.current_remote_path = "/sdcard/Download/"
        self.selected_files = []
        
        # Files List Section
        files_frame = ttk.Labelframe(container, text="전송할 파일", padding="10", bootstyle="info")
        files_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        # Drop zone / Listbox
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=BOTH, expand=YES)
        
        files_scrollbar = ttk.Scrollbar(list_frame, bootstyle="info-round")
        files_scrollbar.pack(side=RIGHT, fill=Y)
        
        files_listbox = tk.Listbox(list_frame, yscrollcommand=files_scrollbar.set, font=("Consolas", 10), selectmode="extended")
        files_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        files_scrollbar.config(command=files_listbox.yview)
        
        # Drop hint
        hint_label = ttk.Label(files_frame, text="파일을 여기에 드래그하세요", font=("Helvetica", 9), bootstyle="secondary", anchor="center")
        hint_label.pack(fill=X, pady=(5, 0))
        
        # Target Path Section
        target_frame = ttk.Labelframe(container, text="대상 경로 선택", padding="10", bootstyle="success")
        target_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        # Path controls
        path_control_frame = ttk.Frame(target_frame)
        path_control_frame.pack(fill=X, pady=(0, 5))
        
        path_label = ttk.Label(path_control_frame, text=self.current_remote_path, font=("Consolas", 10, "bold"))
        path_label.pack(side=LEFT, fill=X, expand=YES)
        
        def refresh_remote_list(path=None):
            if path:
                self.current_remote_path = path
            
            # Update label
            path_label.config(text=self.current_remote_path)
            
            # Clear list
            remote_listbox.delete(0, tk.END)
            remote_listbox.insert(tk.END, ".. (상위 폴더)")
            
            def load_task():
                try:
                    items = self.manager.list_directories(self.selected_device_id, self.current_remote_path)
                    
                    def update_ui(items):
                        for item in items:
                            prefix = "📁 " if item['type'] == 'dir' else "📄 "
                            remote_listbox.insert(tk.END, f"{prefix}{item['name']}")
                            
                    popup.after(0, lambda: update_ui(items))
                except Exception as e:
                    popup.after(0, lambda: messagebox.showerror("에러", f"목록 로딩 실패: {e}"))
            
            threading.Thread(target=load_task).start()
            
        def create_folder():
            from tkinter import simpledialog
            new_folder = simpledialog.askstring("새 폴더", "새 폴더 이름을 입력하세요:", parent=popup)
            if new_folder:
                full_path = f"{self.current_remote_path.rstrip('/')}/{new_folder}"
                try:
                    self.manager.create_directory(self.selected_device_id, full_path)
                    refresh_remote_list()
                except Exception as e:
                    messagebox.showerror("에러", f"폴더 생성 실패: {e}")

        ttk.Button(path_control_frame, text="새 폴더", command=create_folder, bootstyle="outline-success", width=10).pack(side=RIGHT)
        
        # Remote directory list
        remote_list_frame = ttk.Frame(target_frame)
        remote_list_frame.pack(fill=BOTH, expand=YES)
        
        remote_scrollbar = ttk.Scrollbar(remote_list_frame, bootstyle="success-round")
        remote_scrollbar.pack(side=RIGHT, fill=Y)
        
        remote_listbox = tk.Listbox(remote_list_frame, yscrollcommand=remote_scrollbar.set, font=("Consolas", 10))
        remote_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        remote_scrollbar.config(command=remote_listbox.yview)
        
        # Double click to navigate
        def on_remote_dbl_click(event):
            selection = remote_listbox.curselection()
            if not selection: return
            
            text = remote_listbox.get(selection[0])
            
            if text == ".. (상위 폴더)":
                # Move up
                current = self.current_remote_path.rstrip('/')
                parent = os.path.dirname(current)
                if not parent or parent == current: # reached root or issue
                    parent = "/"
                if not parent.endswith('/'): parent += '/'
                refresh_remote_list(parent)
                return
                
            if text.startswith("📁 "):
                folder_name = text[2:].strip() # Remove icon
                new_path = f"{self.current_remote_path.rstrip('/')}/{folder_name}/"
                refresh_remote_list(new_path)
        
        remote_listbox.bind("<Double-Button-1>", on_remote_dbl_click)
        
        # DnD Logic
        def add_files(file_list):
             # Use splitlist to correctly handle Tcl formatted lists
             try:
                 items = self.root.tk.splitlist(file_list)
                 for item in items:
                     if item not in self.selected_files:
                         self.selected_files.append(item)
                         files_listbox.insert(tk.END, item)
             except Exception as e:
                 messagebox.showerror("에러", f"파일 목록 파싱 에러: {e}")
            
        def on_drop(event):
            add_files(event.data)
            
        try:
            popup.drop_target_register("DND_Files")
            popup.dnd_bind("<<Drop>>", on_drop)
        except:
             hint_label.config(text="Drag & Drop 지원되지 않음. 파일 선택 버튼을 사용하세요.")
             
        # Add file button (fallback)
        def browse_files():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(title="파일 선택")
            if files:
                # files is a tuple
                for f in files:
                     if f not in self.selected_files:
                         self.selected_files.append(f)
                         files_listbox.insert(tk.END, f)
                         
        ttk.Button(files_frame, text="파일 추가", command=browse_files, bootstyle="outline-info").pack(pady=5)
        
        # Execute Button
        def start_copy():
            if not self.selected_files:
                messagebox.showwarning("경고", "전송할 파일을 선택하세요.")
                return
            
            total = len(self.selected_files)
            success_count = 0
            
            progress_popup = tk.Toplevel(popup)
            progress_popup.title("전송 중...")
            progress_popup.geometry("300x150")
            
            p_label = ttk.Label(progress_popup, text="준비 중...", anchor="center")
            p_label.pack(pady=20)
            
            p_bar = ttk.Progressbar(progress_popup, maximum=total, bootstyle="success-striped")
            p_bar.pack(fill=X, padx=20)
            
            def copy_task():
                nonlocal success_count
                for i, text in enumerate(self.selected_files):
                    f_path = text
                    
                    p_label.config(text=f"복사 중 ({i+1}/{total}):\n{os.path.basename(f_path)}")
                    p_bar['value'] = i
                    
                    try:
                        self.manager.push_file(self.selected_device_id, f_path, self.current_remote_path)
                        success_count += 1
                    except Exception as e:
                        print(f"Failed to copy {f_path}: {e}")
                
                p_bar['value'] = total
                p_label.config(text="완료!")
                progress_popup.after(1000, progress_popup.destroy)
                popup.after(1000, lambda: messagebox.showinfo("완료", f"{success_count}/{total} 파일 복사 완료"))
                
            threading.Thread(target=copy_task).start()

        ttk.Button(container, text="복사 시작", command=start_copy, bootstyle="success", width=20).pack(pady=10)
        
        # Initial load
        refresh_remote_list()

    def handle_result(self, result):
        if not result:
            self.status_var.set("완료")
            return

        if result.get("type") == "info":
            # Parse and show info
            parsed_info = self.parse_info(result["data"], result.get("title", "정보"))
            messagebox.showinfo(result.get("title", "정보"), parsed_info)
            self.status_var.set(f"완료: {result.get('title')}")
        elif result.get("type") == "action":
            self.status_var.set(result.get("msg", "완료"))
            if "캡쳐 완료" in result.get("msg", ""):
                 messagebox.showinfo("성공", result.get("msg"))

    def handle_error(self, error_msg):
        messagebox.showerror("에러", error_msg)
        self.status_var.set("에러 발생")

    def parse_info(self, raw_data, title):
        """
        Parses raw ADB output into user-friendly text.
        """
        if not raw_data:
            return "정보 없음"

        import re
        
        if "버전 정보" in title:
            # versionName=1.2.3 versionCode=123
            v_name = re.search(r"versionName=([^\s]+)", raw_data)
            v_code = re.search(r"versionCode=(\d+)", raw_data)
            
            info = []
            if v_name: info.append(f"버전 이름: {v_name.group(1)}")
            if v_code: info.append(f"버전 코드: {v_code.group(1)}")
            
            return "\n".join(info) if info else raw_data.strip()

        elif "배터리 정보" in title:
            # level: 100, AC powered: false, status: 2
            info = []
            for line in raw_data.splitlines():
                line = line.strip()
                if line.startswith("level:"):
                    info.append(f"배터리 잔량: {line.split(':')[1].strip()}%")
                elif line.startswith("AC powered:"):
                    val = line.split(':')[1].strip()
                    info.append(f"충전 중: {'예' if val == 'true' else '아니오'}")
                elif line.startswith("USB powered:"):
                    val = line.split(':')[1].strip()
                    if val == 'true': info.append(f"USB 연결됨: 예")
            return "\n".join(info) if info else raw_data.strip()

        elif "최상위 앱 정보" in title:
            # mCurrentFocus=Window{... u0 com.package/.Activity}
            # mFocusedApp=AppWindowToken{... u0 com.package/.Activity ...}
            match = re.search(r"u0\s+([^\s/]+)/\.?([^\s}]+)", raw_data)
            if match:
                return f"패키지: {match.group(1)}\n액티비티: {match.group(2)}"
            return raw_data.strip()

        return raw_data.strip()

    def open_delete_popup(self):
        """
        Opens a popup window with a list of installed packages for deletion.
        """
        popup = tk.Toplevel(self.root)
        popup.title("앱 삭제")
        popup.geometry("500x600")
        
        # Title
        title_label = ttk.Label(popup, text="삭제할 앱을 선택하세요", font=("Helvetica", 14, "bold"), bootstyle="inverse-info")
        title_label.pack(pady=10, padx=10)
        
        # Search box
        search_frame = ttk.Frame(popup)
        search_frame.pack(fill=X, padx=10, pady=5)
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, bootstyle="secondary")
        search_entry.pack(fill=X)
        ttk.Label(search_frame, text="검색:", bootstyle="secondary").pack(side=LEFT, padx=(0, 5))
        search_entry.pack(side=LEFT, fill=X, expand=YES)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(popup)
        list_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame, bootstyle="secondary-round")
        scrollbar.pack(side=RIGHT, fill=Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.config(command=listbox.yview)
        
        # Load packages
        self.status_var.set("패키지 목록 로딩 중...")
        
        def update_item_name(pkg, real_name):
            # Find the item in listbox and update it
            for i in range(listbox.size()):
                item_text = listbox.get(i)
                if f"({pkg})" in item_text:
                    current_name = item_text.split(" (")[0]
                    if current_name != real_name:
                        new_text = f"{real_name} ({pkg})"
                        listbox.delete(i)
                        listbox.insert(i, new_text)
                        # Update map
                        self.package_map[new_text] = pkg
                    break

        def fetch_real_names(packages):
            import concurrent.futures
            
            # Filter first to only fetch relevant apps
            target_packages = [
                pkg for pkg, _ in packages 
                if pkg.startswith("com.wjthinkbig") or pkg.startswith("air.com.wjthinkbig")
            ]
            
            def get_label(pkg):
                real_name = self.manager.get_app_label(self.selected_device_id, pkg)
                return pkg, real_name

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_pkg = {executor.submit(get_label, pkg): pkg for pkg in target_packages}
                
                count = 0
                total = len(target_packages)
                
                for future in concurrent.futures.as_completed(future_to_pkg):
                    pkg, real_name = future.result()
                    if real_name:
                        # Update UI
                        popup.after(0, lambda p=pkg, n=real_name: update_item_name(p, n))
                    
                    count += 1
                    popup.after(0, lambda c=count, t=total: self.status_var.set(f"이름 로딩 중... ({c}/{t})"))

            popup.after(0, lambda: self.status_var.set(f"총 {len(target_packages)}개 패키지 (로딩 완료)"))

        def populate_list(packages):
            # Create a mapping of display text to package name
            self.package_map = {}
            listbox.delete(0, tk.END)
            
            # Filter packages to show only wjthinkbig apps
            filtered_packages = [
                (pkg, app_name) for pkg, app_name in packages 
                if pkg.startswith("com.wjthinkbig") or pkg.startswith("air.com.wjthinkbig")
            ]
            
            for pkg, app_name in filtered_packages:
                # Format: "AppName (com.example.myapp)"
                display_text = f"{app_name} ({pkg})"
                self.package_map[display_text] = pkg
                listbox.insert(tk.END, display_text)
            
            self.status_var.set(f"총 {len(filtered_packages)}개 패키지 (이름 불러오는 중...)")
            
            # Search filter
            def filter_packages(*args):
                search_text = search_var.get().lower()
                listbox.delete(0, tk.END)
                for display_text, pkg in self.package_map.items():
                    if search_text in display_text.lower():
                        listbox.insert(tk.END, display_text)
            
            search_var.trace('w', filter_packages)

        def load_packages():
            try:
                # 1. Get package list first (fast)
                packages = self.manager.get_installed_packages(self.selected_device_id)
                popup.after(0, lambda: populate_list(packages))
                
                # 2. Fetch real app names in background
                threading.Thread(target=lambda: fetch_real_names(packages), daemon=True).start()
                
            except Exception as e:
                popup.after(0, lambda: messagebox.showerror("에러", f"패키지 목록 로딩 실패: {e}"))
                popup.after(0, popup.destroy)
        
        # Delete button
        def show_app_details():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "앱을 선택해주세요.")
                return
            
            display_text = listbox.get(selection[0])
            package = self.package_map.get(display_text, display_text)
            
            # Open app details popup
            self.show_app_detail_popup(package, popup)
        
        # Bind double-click to show details
        listbox.bind("<Double-Button-1>", lambda e: show_app_details())
        
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="닫기", command=popup.destroy, bootstyle="secondary").pack(expand=YES, fill=X, padx=5)
        
        # Start loading in background
        threading.Thread(target=load_packages).start()

    def show_app_detail_popup(self, package_name, parent_popup):
        """
        Shows detailed information about an app with delete option.
        """
        detail_popup = tk.Toplevel(self.root)
        detail_popup.title("앱 상세 정보")
        detail_popup.geometry("500x600")
        
        # Title
        title_label = ttk.Label(detail_popup, text="앱 정보 로딩 중...", font=("Helvetica", 14, "bold"), bootstyle="inverse-info")
        title_label.pack(pady=10, padx=10)
        
        # Info frame with scrollbar
        info_frame = ttk.Frame(detail_popup)
        info_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Text widget for displaying info
        text_widget = tk.Text(info_frame, wrap=tk.WORD, font=("Consolas", 10), height=20)
        text_widget.pack(side=LEFT, fill=BOTH, expand=YES)
        
        scrollbar = ttk.Scrollbar(info_frame, command=text_widget.yview, bootstyle="secondary-round")
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Load app details in background
        def load_details():
            try:
                details = self.manager.get_app_details(self.selected_device_id, package_name)
                detail_popup.after(0, lambda: display_details(details))
            except Exception as e:
                detail_popup.after(0, lambda: messagebox.showerror("에러", f"앱 정보 로딩 실패: {e}"))
                detail_popup.after(0, detail_popup.destroy)
        
        def display_details(details):
            title_label.config(text=details.get("name", "알 수 없음"))
            
            # Format and display details
            info_text = f"""패키지명: {details.get('package', 'N/A')}

앱 이름: {details.get('name', 'N/A')}

버전 이름: {details.get('version_name', 'N/A')}

버전 코드: {details.get('version_code', 'N/A')}

설치 날짜: {details.get('install_date', 'N/A')}

업데이트 날짜: {details.get('update_date', 'N/A')}

데이터 디렉토리: {details.get('data_dir', 'N/A')}

APK 경로: {details.get('apk_path', 'N/A')}
"""
            
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
        
        # Delete button
        def delete_app():
            if messagebox.askyesno("확인", f"다음 앱을 삭제하시겠습니까?\n\n{package_name}"):
                detail_popup.destroy()
                parent_popup.destroy()
                self.status_var.set(f"삭제 중: {package_name}")
                
                def task():
                    try:
                        result = self.manager.execute_action(10, self.selected_device_id, package=package_name)
                        self.root.after(0, lambda: self.handle_result(result))
                    except Exception as e:
                        self.root.after(0, lambda: self.handle_error(str(e)))
                
                threading.Thread(target=task).start()
        
        btn_frame = ttk.Frame(detail_popup)
        btn_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="삭제", command=delete_app, bootstyle="danger").pack(side=LEFT, expand=YES, fill=X, padx=5)
        ttk.Button(btn_frame, text="닫기", command=detail_popup.destroy, bootstyle="secondary").pack(side=RIGHT, expand=YES, fill=X, padx=5)
        
        # Start loading
        threading.Thread(target=load_details).start()

    def show_help(self):
        """
        Shows help dialog for connecting devices.
        """
        help_text = """디바이스 연결 방법

1. 디바이스에서 개발자 옵션 활성화:
   - 설정 > 디바이스 정보 > 빌드 번호를 7번 연속 탭

2. USB 디버깅 활성화:
   - 설정 > 개발자 옵션 > USB 디버깅 켜기

3. USB 케이블로 디바이스를 컴퓨터에 연결

4. 디바이스에서 "USB 디버깅 허용" 팝업이 나타나면 '허용' 선택

5. '새로고침' 버튼을 눌러 디바이스 목록 갱신

문제 해결:
- 디바이스가 보이지 않으면 USB 케이블을 다시 연결해보세요
- ADB 드라이버가 설치되어 있는지 확인하세요
- 일부 디바이스는 '파일 전송(MTP)' 모드로 설정해야 합니다
"""
        messagebox.showinfo("도움말", help_text)
