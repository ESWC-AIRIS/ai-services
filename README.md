# GazeHome AI Services

**스마트 홈 AI 추천 및 제어 시스템**

LG 스마트 가전과 연동하여 AI가 상황에 맞는 스마트 기기 제어를 추천하고, 사용자 확인 후 실제 기기를 제어하는 통합 솔루션입니다.

## 🔥 시스템 개요

GazeHome AI 서버는 다음과 같은 흐름으로 작동합니다:

1. **AI 추천 생성**: 시간대, 계절, 기기 상태를 고려한 스마트 추천 생성
2. **Hardware 컨펌**: 사용자에게 YES/NO 확인 요청
3. **기기 제어**: 사용자 승인 시 Gateway를 통해 실제 LG 기기 제어
4. **상태 기반 스마트 액션**: 기기 현재 상태에 따라 적절한 액션 결정

> 🎯 **핵심 특징**: AI가 추천 생성 시점에 기기 제어 정보를 미리 준비하여 효율적인 플로우 구현

## 🚀 주요 기능

- **스마트 AI 추천**: 시간대, 계절, 기기 상태를 고려한 지능형 추천 생성
- **Gateway 연동**: LG ThinQ Gateway를 통한 실제 스마트 기기 제어
- **상태 기반 액션**: 기기 현재 상태에 따른 스마트 액션 결정
- **자동 스케줄러**: 주기적 AI 추천 생성 (30분 간격, 설정 가능)
- **Hardware 연동**: 사용자 확인을 위한 Hardware 서버 통신
- **실시간 기기 상태**: Gateway에서 실시간 기기 상태 조회 및 반영

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python
- **LLM**: LangChain + Gemini API
- **Database**: MongoDB
- **Gateway**: LG ThinQ Gateway API
- **Hardware**: Mock/실제 Hardware 서버
- **Scheduler**: 백그라운드 작업 스케줄러
- **Deployment**: Uvicorn

## Python 버전 호환성

- **Python 3.9**: 권장 버전
- **Python 3.10 ~ 3.12** : 완전 호환

> 💡 **권장사항**: 개발할때는 Python 3.10.11을 이용했습니다.

## 📚 문서

프로젝트 관련 상세 문서들은 `Docs/` 폴더에서 확인할 수 있습니다:

- [`smart_recommendation_flow.md`](Docs/smart_recommendation_flow.md) - 스마트 추천 플로우 상세 설명
- [`demo_execution_guide.md`](Docs/demo_execution_guide.md) - 데모 실행 가이드 (대회용 vs 개발용)
- [`terminal_execution_guide.md`](Docs/terminal_execution_guide.md) - 터미널 3개로 전체 플로우 테스트
- [`git_convention.md`](Docs/git_convention.md) - Git 커밋 컨벤션 가이드
- [`venv_and_requirements_guide.md`](Docs/venv_and_requirements_guide.md) - 가상환경 및 의존성 관리 가이드

## 🚀 빠른 시작

### 1. 가상환경 설정 및 의존성 설치
```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
source .venv/Scripts/activate  # Windows
source .venv/bin/activate       # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일을 편집하여 필요한 설정들을 구성
# - GEMINI_API_KEY: Google Gemini API 키
# - MONGODB_URI: MongoDB 연결 URI
# - GATEWAY_URL: LG ThinQ Gateway URL (실제 서버)
# - HARDWARE_URL: Hardware 서버 URL (Mock 또는 실제)
# - SCHEDULER_AUTO_START: 스케줄러 자동 시작 여부 (true/false)
```

### 3. 서버 실행
```bash
# 방법 1: uvicorn 직접 실행 (권장)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: main.py 실행
python main.py
```

### 4. 시스템 상태 확인
```bash
curl http://localhost:8000/health
```

예상 응답:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00+09:00",
  "message": "GazeHome AI Services 정상 작동 중"
}
```

### 5. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. 테스트 실행

#### 🎯 전체 플로우 테스트 (권장)
```bash
# 터미널 3개로 전체 플로우 테스트
# 자세한 방법은 Docs/terminal_execution_guide.md 참조
python examples/run_demo.py
```

#### 🏠 스마트 홈 데모
```bash
# 기상 조건 및 시간대별 시나리오 테스트
python examples/run_demo.py
```

#### 🔧 Mock 서버 테스트
```bash
# Mock Hardware 서버 실행
python examples/mock_servers.py
```

## 📡 주요 API 엔드포인트

### POST /api/recommendations
AI가 스마트 추천을 생성하고 Hardware에 전송합니다.

**요청 예시:**
```json
{
  "title": "에어컨 켤까요?",
  "contents": "현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다."
}
```

**응답 예시:**
```json
{
  "message": "AI 추천: 에어컨 켤까요? - 현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다.",
  "confirm": "YES",
  "device_control": {
    "device_id": "ac_001",
    "device_type": "air_conditioner",
    "action": "turn_on",
    "device_alias": "거실 에어컨"
  }
}
```

### POST /api/devices/control
Gateway를 통해 LG 스마트 기기를 제어합니다.

**요청 예시:**
```json
{
  "device_id": "ac_001",
  "action": "turn_on"
}
```

**응답 예시:**
```json
{
  "message": "[GATEWAY] 스마트 기기 제어(에어컨) 완료"
}
```

### GET /scheduler/status
스케줄러 상태를 확인합니다.

### POST /scheduler/start
스케줄러를 시작합니다.

### POST /scheduler/stop
스케줄러를 중지합니다.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해 주세요.