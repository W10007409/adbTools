# WJ Pad Controller 배포 가이드

## 배포 패키지 정보

### 파일 구조

**onefile 방식 - 단일 실행 파일**

```
dist/
├── WJ_Pad_Controller.exe  (92MB) - 단일 실행 파일 (모든 것 포함)
└── README.md               (선택사항) - 사용자 가이드
```

**포함된 내용**:
- Python 런타임 및 모든 라이브러리
- exec/ 폴더 (adb.exe, scrcpy.exe 등)
- adb_tool 애플리케이션 코드
- tkinterdnd2 드래그앤드롭 라이브러리
- NumPy, PIL 등 모든 의존성

**실행 시 동작**:
- 첫 실행 시 임시 폴더에 자동 압축 해제 (C:\Users\사용자명\AppData\Local\Temp\_MEI*)
- 압축 해제된 파일로 프로그램 실행
- 프로그램 종료 시 임시 파일 자동 정리

### 배포 파일 위치

```
f:\MyWorkSpace\adbTools\dist\WJ_Pad_Controller.exe (92MB)
```

## 빌드 프로세스

### 1. 사전 준비

필수 패키지 설치:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 빌드 실행

```bash
# 기존 빌드 삭제 후 새로 빌드
pyinstaller WJ_Pad_Controller.spec --clean
```

### 3. 배포 패키지 생성

빌드가 완료되면 `dist/WJ_Pad_Controller/` 폴더가 자동으로 생성됩니다.

README.md 파일 추가 (선택사항):
```bash
# 사용자 가이드를 배포 폴더에 복사
cp README_FOR_USERS.md dist/WJ_Pad_Controller/README.md
```

## 배포 방법

### 방법 1: 직접 배포 (권장)

**`WJ_Pad_Controller.exe` 파일 하나만 공유**

- 이메일 첨부
- USB 드라이브 복사
- 네트워크 공유 폴더
- 클라우드 스토리지 (Google Drive, OneDrive 등)

**장점**:
- 단일 파일이므로 배포가 매우 간단
- 별도의 설치나 압축 해제 불필요
- 사용자가 받아서 바로 실행 가능

### 방법 2: ZIP 압축 (선택사항)

README와 함께 배포하려면:

```bash
# PowerShell에서 실행
cd dist
Compress-Archive -Path "WJ_Pad_Controller.exe", "README.md" -DestinationPath "WJ_Pad_Controller_v1.0.0.zip" -Force
```

### 방법 3: 네트워크 공유

```bash
# 네트워크 드라이브에 복사
copy dist\WJ_Pad_Controller.exe \\network-share\tools\
```

## 배포 체크리스트

- [x] PyInstaller 빌드 성공
- [x] 단일 exe 파일 생성 확인 (WJ_Pad_Controller.exe, 92MB)
- [x] exec 폴더 포함 확인 (내장됨)
- [x] tkinterdnd2 라이브러리 포함 확인 (내장됨)
- [x] 모든 의존성 포함 확인 (onefile 방식)
- [x] README.md 작성 완료
- [ ] 실제 기기에서 테스트 실행
- [ ] Windows Defender 예외 설정 가이드
- [ ] 사용자 교육 자료 준비
- [ ] 버전 관리 시스템에 태그 생성

## 사용자 배포 안내

### 사용자에게 전달할 내용

**매우 간단합니다!**

1. **받기**
   - `WJ_Pad_Controller.exe` 파일 다운로드 또는 복사

2. **실행**
   - 원하는 위치에 파일 복사 (설치 불필요)
   - `WJ_Pad_Controller.exe` 더블클릭
   - Windows Defender 경고 시 "추가 정보" > "실행" 클릭

3. **사용**
   - USB로 기기 연결
   - 프로그램에서 자동으로 기기 감지
   - 원하는 기능 사용

**참고**:
- 첫 실행 시 3-5초 정도 로딩 시간이 있습니다 (정상)
- 두 번째 실행부터는 빠르게 시작됩니다

## 버전 관리

### 현재 버전
- **버전**: 1.0.0
- **빌드 날짜**: 2025-11-21
- **파일 크기**: 92MB
- **배포 방식**: onefile (단일 실행 파일)
- **빌드 환경**:
  - Python: 3.10.4
  - PyInstaller: 6.9.0
  - ttkbootstrap: 1.19.0
  - tkinterdnd2: 0.4.3

### 다음 버전 빌드 시

1. `setup.py`에서 버전 번호 업데이트
2. 변경 사항을 CHANGELOG.md에 기록
3. Git 태그 생성: `git tag v1.0.1`
4. 빌드 재실행
5. 새 배포 패키지 생성

## 문제 해결

### 빌드 실패 시

1. **의존성 확인**
   ```bash
   pip list | findstr -i "pyinstaller ttkbootstrap tkinterdnd2"
   ```

2. **캐시 삭제**
   ```bash
   pyinstaller WJ_Pad_Controller.spec --clean
   ```

3. **가상 환경 재생성**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### 실행 파일 크기가 큰 경우

현재 크기: 92MB (onefile 방식)

**크기 분석**:
- exec 폴더 (adb, scrcpy): ~70MB
- Python 런타임 및 라이브러리: ~15MB
- NumPy, PIL 등: ~7MB

**크기 최적화 옵션**:
1. onedir 방식으로 전환 (폴더 배포, 하지만 파일 많음)
2. 불필요한 대형 라이브러리 제외 (NumPy, PIL 등)
3. UPX 압축 (이미 적용됨)

**참고**:
- onefile 방식의 편의성을 고려하면 92MB는 합리적인 크기입니다
- exec 폴더의 scrcpy가 큰 비중을 차지합니다

### Windows Defender 차단 문제

사용자에게 안내:
1. "추가 정보" 클릭
2. "실행" 버튼 클릭
3. 또는 Windows Defender 예외 목록에 추가

## 보안 고려사항

1. **코드 서명**
   - 선택사항: Authenticode 코드 서명 인증서 사용
   - Windows SmartScreen 경고 방지

2. **바이러스 검사**
   - 배포 전 VirusTotal 등으로 검사

3. **업데이트 메커니즘**
   - 자동 업데이트 기능 추가 고려 (향후 버전)

## 참고 자료

- PyInstaller 공식 문서: https://pyinstaller.org/
- ttkbootstrap 문서: https://ttkbootstrap.readthedocs.io/
- ADB 공식 문서: https://developer.android.com/tools/adb
- scrcpy 프로젝트: https://github.com/Genymobile/scrcpy

---

**작성일**: 2025-11-21
**작성자**: AI 빌드 시스템
**상태**: 배포 준비 완료
