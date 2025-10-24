# [개발용] 터미널 3개로 AI서버 돌아가는거 확인하기

## 개요
AI 서버, Mock Hardware 서버, 실제 Gateway를 연결하여 전체 추천 플로우를 테스트하는 방법을 설명합니다.

## 사전 준비
- 가상환경이 설정되어 있어야 합니다
- `.env` 파일이 올바르게 설정되어 있어야 합니다
- 실제 Gateway URL이 설정되어 있어야 합니다

## 실행 순서

### 1단계: 가상환경 활성화
```bash
source .venv/Scripts/activate
```

### 2단계: Mock Hardware 서버 실행
**터미널 1**에서 실행:
```bash
python examples/mock_servers.py
```
- 이 명령어를 실행하면 Mock 서버가 시작됩니다
- 터미널을 그대로 두세요 (백그라운드로 계속 실행)

### 3단계: AI 서버 실행
**새 터미널 창**을 열고:
```bash
cd /c/Users/Administrator/OneDrive/문서/ESWC-AIRIS/ai-services
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- AI 서버가 시작됩니다
- 터미널을 그대로 두세요 (백그라운드로 계속 실행)

### 4단계: 전체 플로우 테스트
**새 터미널 창**을 열고:
```bash
cd /c/Users/Administrator/OneDrive/문서/ESWC-AIRIS/ai-services
source .venv/Scripts/activate
python examples/run_demo.py
```

## 실행 결과
이렇게 하면 다음 플로우가 테스트됩니다:
1. **AI 추천 생성** → AI 서버에서 스마트 추천 생성
2. **Hardware 컨펌** → Mock Hardware 서버에서 사용자 응답 (YES/NO)
3. **AI 기기 제어** → AI 서버에서 실제 Gateway를 통해 기기 제어

## 터미널 구성
- **터미널 1**: Mock Hardware 서버 (포트 8080)
- **터미널 2**: AI 서버 (포트 8000)
- **터미널 3**: 데모 실행 (전체 플로우 테스트)

## 주의사항
- 각 터미널은 백그라운드로 계속 실행되어야 합니다
- 터미널을 닫으면 해당 서버가 종료됩니다
- 서버 실행 순서를 지켜주세요

## 문제 해결
- **포트 충돌**: 다른 포트를 사용하는 서비스가 있는지 확인
- **가상환경 오류**: `source .venv/Scripts/activate` 명령어가 올바른지 확인
- **경로 오류**: 현재 디렉토리가 올바른지 확인

## 종료 방법
각 터미널에서 `Ctrl+C`를 눌러 서버를 종료할 수 있습니다.
