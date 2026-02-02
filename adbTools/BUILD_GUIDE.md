# WJ Pad Controller 배포 가이드

## 필요한 패키지 설치

먼저 PyInstaller를 설치합니다:

```bash
pip install pyinstaller
```

## 실행 파일 빌드

### 방법 1: spec 파일 사용 (권장)

```bash
pyinstaller WJ_Pad_Controller.spec
```

### 방법 2: 직접 명령어 사용

```bash
pyinstaller --name="WJ_Pad_Controller" ^
    --windowed ^
    --add-data "exec;exec" ^
    --hidden-import=tkinter ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=tkinterdnd2 ^
    adb_tool\main.py
```

## 빌드 결과

빌드가 완료되면 다음 디렉토리가 생성됩니다:

- `dist/WJ_Pad_Controller/` - 배포용 폴더
  - `WJ_Pad_Controller.exe` - 실행 파일
  - `exec/` - adb 및 scrcpy 도구
  - 기타 필요한 라이브러리 파일들

## 배포 방법

`dist/WJ_Pad_Controller/` 폴더 전체를 압축하여 배포하면 됩니다.

사용자는 압축을 풀고 `WJ_Pad_Controller.exe`를 실행하면 됩니다.

## 주의사항

1. **exec 디렉토리**: adb.exe와 scrcpy.exe가 포함되어 있어야 합니다
2. **관리자 권한**: ADB 명령어 실행을 위해 관리자 권한이 필요할 수 있습니다
3. **Windows Defender**: 처음 실행 시 Windows Defender가 차단할 수 있습니다

## 단일 파일로 빌드 (선택사항)

모든 것을 하나의 exe 파일로 만들려면:

```bash
pyinstaller --name="WJ_Pad_Controller" ^
    --onefile ^
    --windowed ^
    --add-data "exec;exec" ^
    --hidden-import=tkinter ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=tkinterdnd2 ^
    adb_tool\main.py
```

**참고**: 단일 파일 모드는 실행 시 압축 해제 시간이 필요하므로 시작이 느릴 수 있습니다.

## 아이콘 추가 (선택사항)

아이콘 파일(.ico)이 있다면:

```bash
pyinstaller WJ_Pad_Controller.spec --icon=icon.ico
```

또는 spec 파일의 `icon=None` 부분을 `icon='icon.ico'`로 수정합니다.
