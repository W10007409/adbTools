# WJ Pad Controller (ADB Tools)

**WJ Pad Controller**는 웅진북클럽 패드(Android 디바이스)를 PC에서 손쉽게 관리하고 제어하기 위해 개발된 윈도우 데스크탑 애플리케이션입니다.

이 도구는 ADB(Android Debug Bridge)를 기반으로 작동하며, 복잡한 커맨드 라인 명령 없이 직관적인 GUI환경에서 디바이스 제어, 앱 관리, 파일 전송, 로그 확인 등의 작업을 수행할 수 있습니다.

## 주요 기능 (Key Features)

### 1. 디바이스 제어 (Device Control)
- **화면 미러링 (Scrcpy)**: 연결된 디바이스의 화면을 PC에서 실시간으로 확인하고 제어합니다.
- **기본 키 입력**: 뒤로가기, 홈 버튼, 화면 끄기/켜기 등의 하드웨어 키 동작을 수행합니다.
- **화면 캡쳐**: 디바이스 화면을 캡쳐하여 PC로 저장합니다.
- **멀티 디바이스 제어**: 모든 디바이스의 화면을 동시에 끄거나 미러링할 수 있습니다.

### 2. 앱 관리 (App Management)
- **앱 설치 (APK Install)**: APK 파일을 드래그 앤 드롭하여 간편하게 설치할 수 있습니다.
- **앱 삭제 (App Delete)**: 설치된 패키지 목록을 조회하고 선택하여 삭제할 수 있습니다. (검색 기능 지원)
- **앱 정보 확인**: 버전 코드, 설치 날짜 등 앱 상세 정보를 확인할 수 있습니다.

### 3. 파일 관리 (File Management)
- **파일 복사 (PC -> Device)**: PC의 파일을 드래그 앤 드롭으로 디바이스의 특정 경로로 복사합니다.
- **폴더 탐색**: 디바이스 내 폴더 구조를 탐색하고 새 폴더를 생성할 수 있습니다.

### 4. 개발 및 디버깅 도구 (Debugging)
- **로그캣 (Logcat)**: 실시간 시스템 로그를 확인하거나 파일로 저장할 수 있습니다.
- **정보 조회**: 런처 버전, 배터리 정보, 최상위 실행 앱 정보 등을 조회합니다.
- **브로드캐스트 전송**: 특정 인텐트 브로드캐스트를 전송하여 테스트할 수 있습니다.

---

## 개발 환경 설정 (Development Setup)

이 프로젝트를 수정하거나 실행하기 위한 개발 환경 설정 방법입니다.

### 요구 사항 (Prerequisites)
- **Python 3.8 이상**
- **ADB 및 Scrcpy 실행 파일**: 프로젝트 내 `exec/` 폴더에 `adb.exe`와 `scrcpy.exe` 등의 바이너리 파일이 위치해야 합니다.

### 설치 및 실행

1. **저장소 클론 (Clone Repository)**
   ```bash
   git clone https://github.com/W10007409/adbTools.git
   cd adbTools
   ```

2. **가상 환경 생성 (권장)**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   ```

3. **의존성 설치 (Install Dependencies)**
   ```bash
   pip install -r requirements.txt
   ```
   *(참고: `tkinterdnd2`, `ttkbootstrap` 등의 패키지가 필요합니다.)*

4. **애플리케이션 실행**
   ```bash
   python find_tkdnd.py # 필요시 tkdnd 경로 확인
   python -m adb_tool.main
   # 또는
   python adb_tool/main.py
   ```

---

## 배포용 빌드 방법 (Building Executable)

PyInstaller를 사용하여 단독 실행 가능한 `.exe` 파일로 빌드할 수 있습니다.

### 빌드 명령
이미 작성된 `WJ_Pad_Controller.spec` 파일을 사용하여 빌드하는 것을 권장합니다.

```bash
pyinstaller WJ_Pad_Controller.spec
```

### 빌드 결과물
빌드가 완료되면 `dist/WJ_Pad_Controller/` 폴더 내에 실행 파일이 생성됩니다. 이 폴더 전체를 배포하면 됩니다.

---

## 프로젝트 구조

```
adbTools/
├── adb_tool/              # 소스 코드 디렉토리
│   ├── adb_manager.py     # ADB 명령 실행 및 로직 처리
│   ├── gui.py             # UI 구성 (Tkinter/ttkbootstrap)
│   ├── main.py            # 진입점 (Entry Point)
│   └── utils.py           # 유틸리티 함수
├── exec/                  # 외부 실행 파일 (adb, scrcpy 등)
├── WJ_Pad_Controller.spec # PyInstaller 빌드 설정 파일
├── BUILD_GUIDE.md         # 상세 빌드 가이드
└── requirements.txt       # 파이썬 의존성 목록
```
