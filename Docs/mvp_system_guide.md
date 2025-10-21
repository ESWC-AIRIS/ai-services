# GazeHome AI MVP 시스템 가이드

**HW-AI-Gateway 통신을 위한 MVP 수준의 깔끔한 아키텍처**

## 🎯 시스템 개요

이 MVP 시스템은 하드웨어, AI 서버, Gateway 간의 통신을 위한 깔끔한 API 구조를 제공합니다.

### 주요 기능

1. **기기 제어 (Direct Control)**: HW → AI → Gateway
2. **기기 제어 추천 (Smart Recommendation)**: AI → HW → AI → Gateway

## 🏗️ 아키텍처

```
┌─────────────┐    HTTP    ┌─────────────┐    HTTP    ┌─────────────┐
│ Hardware    │ ────────► │ AI Server   │ ────────► │ Gateway     │
│ (User)      │           │ (Port 8000) │           │ (Port 9000) │
└─────────────┘           └─────────────┘           └─────────────┘
                                │
                                │ HTTP
                                ▼
                         ┌─────────────┐
                         │ Hardware    │
                         │ (Feedback)  │
                         └─────────────┘
```

## 📡 API 엔드포인트

### 1. HW → AI: 스마트기기 단순 제어

**엔드포인트**: `POST /api/lg/control`

**요청**:
```json
{
    "device_id": "b403...",
    "action": "turn_on"
}
```

**응답**:
```json
{
    "message": "[AI] 스마트 기기 단순 제어 완료",
    "device_id": "b403...",
    "action": "turn_on",
    "timestamp": "2024-01-01T12:00:00+09:00"
}
```

**지원 액션**: `turn_on`, `turn_off`, `clean`, `auto`

### 2. AI → HW: 추천 문구 전달

**엔드포인트**: `POST /api/recommendations/recommendations`

**요청**:
```json
{
    "message": "에어컨 킬까요?"
}
```

**응답**:
```json
{
    "message": "추천 문구 유저 피드백",
    "confirm": "YES"
}
```

**지원 응답**: `YES`, `NO`

### 3. AI → Gateway: LG Thinq 조작

**내부적으로 AI 서버가 Gateway로 전달**:
```json
{
    "device_id": "b403...",
    "action": "turn_on"
}
```

## 🚀 실행 방법

### 1. 기본 실행

```bash
# AI 서버 시작
python main.py --mode gcp-dev

# 별도 터미널에서 Mock 서버들 시작
python examples/mock_servers.py

# 별도 터미널에서 테스트 실행
python examples/test_mvp_system.py
```

### 2. 통합 데모 실행

```bash
# 모든 서버와 테스트를 자동으로 실행
python examples/run_demo.py
```

## 🧪 테스트 시나리오

### 시나리오 1: 직접 제어
1. 하드웨어에서 AI 서버로 제어 요청
2. AI 서버가 Gateway로 제어 명령 전달
3. Gateway에서 실제 기기 제어 실행

### 시나리오 2: 추천 기반 제어
1. AI가 사용자에게 추천 문구 전송
2. 사용자가 허가/거부 응답
3. 허가 시 AI가 Gateway로 제어 명령 전달

### 시나리오 3: 다양한 기기 제어
- 에어컨: 켜기/끄기/자동모드
- 조명: 켜기/끄기
- TV: 켜기/끄기
- 공기청정기: 켜기/끄기/청소/자동

## 📁 파일 구조

```
ai-services/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── lg_control.py          # HW → AI → Gateway
│   │   │   └── smart_recommendations.py # AI → HW
│   │   └── router.py                   # 라우터 설정
│   └── main.py                        # FastAPI 앱
├── examples/
│   ├── test_mvp_system.py            # MVP 테스트
│   ├── mock_servers.py               # Mock 서버들
│   └── run_demo.py                   # 통합 데모
└── Docs/
    └── mvp_system_guide.md           # 이 가이드
```

## 🔧 설정

### 환경 변수

```bash
# AI 서버 설정
export GATEWAY_ENDPOINT="http://localhost:9000/api/lg/control"
export HARDWARE_ENDPOINT="http://localhost:8080/api/recommendations"

# 포트 설정
export AI_SERVER_PORT=8000
export HARDWARE_PORT=8080
export GATEWAY_PORT=9000
```

### 설정 파일

`app/core/config.py`에서 엔드포인트 설정:

```python
class Settings(BaseSettings):
    GATEWAY_ENDPOINT: str = "http://localhost:9000/api/lg/control"
    HARDWARE_ENDPOINT: str = "http://localhost:8080/api/recommendations"
```

## 📊 모니터링

### 상태 확인

```bash
# AI 서버 상태
curl http://localhost:8000/health

# LG 제어 상태
curl http://localhost:8000/api/lg/status

# 추천 시스템 상태
curl http://localhost:8000/api/recommendations/status
```

### 로그 확인

```bash
# AI 서버 로그
tail -f logs/ai_server.log

# Mock 서버 로그
tail -f logs/mock_servers.log
```

## 🐛 문제 해결

### 일반적인 문제

1. **포트 충돌**: 다른 서비스가 같은 포트를 사용 중
   ```bash
   # 포트 사용 확인
   netstat -tulpn | grep :8000
   ```

2. **연결 실패**: 서버가 아직 시작되지 않음
   ```bash
   # 서버 시작 대기
   sleep 10
   ```

3. **API 오류**: 요청 형식이 잘못됨
   ```bash
   # API 문서 확인
   curl http://localhost:8000/docs
   ```

### 디버깅

```bash
# 상세 로그로 실행
PYTHONPATH=. python main.py --mode gcp-dev --log-level debug

# 테스트만 실행
PYTHONPATH=. python examples/test_mvp_system.py
```

## 🎉 성공 확인

데모가 성공적으로 실행되면 다음과 같은 메시지를 볼 수 있습니다:

```
🎉 모든 테스트 통과!
  ✅ HW → AI → Gateway (직접 제어)
  ✅ AI → HW → AI → Gateway (추천 기반 제어)
  ✅ 다양한 시나리오

🚀 MVP 시스템이 정상적으로 작동하고 있습니다!
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. 모든 서버가 정상적으로 시작되었는지
2. 포트가 충돌하지 않는지
3. API 요청 형식이 올바른지
4. 로그에서 오류 메시지 확인

---

**GazeHome AI MVP 시스템** - 깔끔하고 효율적인 HW-AI-Gateway 통신 🚀
