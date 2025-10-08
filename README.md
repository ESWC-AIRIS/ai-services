# GazeHome AI Services

**시선으로 제어하는 스마트 홈 AI 서버**

아이트래킹 기술과 대형 언어 모델을 결합하여, 사용자의 시선만으로 LG 스마트 가전 및 다양한 IoT 기기를 직관적으로 제어할 수 있는 AIoT 통합 솔루션입니다.

## 🔥 시스템 개요

GazeHome AI 서버는 다음과 같은 흐름으로 작동합니다:

1. **하드웨어**: 사용자가 시선으로 IoT 기기를 클릭 (예: "에어컨을 클릭했다")
2. **AI 서버**: 클릭된 기기 정보를 받아 LLM Agent로 분석
3. **의도 추론**: 사용자의 심층적 의도 파악 (시간대, 기기 상태, 환경 고려)
4. **추천 생성**: 최적의 다음 명령어 추천
5. **응답 반환**: 하드웨어에 추천 정보 전송

> 💾 **MongoDB 저장**: 데이터 모델은 준비되어 있지만 실제 저장은 선택사항입니다.  
> 필요시 `gaze.py`의 주석을 해제하여 활성화할 수 있습니다.

> 💡 **2025-10-08 업데이트**: x, y 좌표 기반 시선 추적에서 **클릭된 IoT 기기 정보 직접 수신** 방식으로 변경되었습니다.  
> 자세한 내용은 [`Docs/system_update_summary.md`](Docs/system_update_summary.md)를 참조하세요.

## 🚀 주요 기능

- **기기 클릭 이벤트 처리**: 하드웨어에서 전송한 클릭된 IoT 기기 정보 수신
- **심층적 의도 추론**: LLM을 활용한 정확한 사용자 의도 분석
- **맥락 기반 추천**: 시간대, 기기 상태, 환경 정보를 고려한 최적 명령어 생성
- **자동화 플래너**: 최적의 제어 시나리오 자동 설계
- **실시간 반영**: 사용자 이력, 날씨, 일정 등 실시간 정보 반영
- **품질 관리**: LangSmith/LangFuse를 통한 LLM 추론 모니터링

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python
- **LLM**: LangChain + Gemini API
- **Database**: MongoDB
- **Vector DB**: ChromaDB (RAG)
- **Monitoring**: LangSmith, LangFuse
- **Deployment**: Uvicorn

## 📚 문서

프로젝트 관련 상세 문서들은 `Docs/` 폴더에서 확인할 수 있습니다:

- [`api_documentation.md`](Docs/api_documentation.md) - API 엔드포인트 문서 및 테스트 가이드
- [`gazehome_architecture.md`](Docs/gazehome_architecture.md) - GazeHome AI 서버 아키텍처 및 구조 문서
- [`agent_architecture.md`](Docs/agent_architecture.md) - GazeHome AI 에이전트 시스템 아키텍처 문서
- [`weather_mcp_guide.md`](Docs/weather_mcp_guide.md) - Weather MCP 구현 및 사용 가이드
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
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키들을 설정
# - GEMINI_API_KEY: Google Gemini API 키
# - MONGODB_URI: MongoDB 연결 URI
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
curl http://localhost:8000/api/gaze/status
```

예상 응답:
```json
{
  "status": "active",
  "timestamp": "2024-01-15T14:30:00+09:00",
  "message": "시선 클릭 기반 IoT 제어 시스템 정상 작동 중",
  "mode": "device_click"
}
```

### 5. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. 테스트 실행

#### 🧪 전체 시스템 테스트 (권장)
```bash
# MCP + LLM + 추천 시스템 통합 테스트
PYTHONPATH=. python examples/test_full_system.py
```

#### 🌤️ 날씨 MCP 테스트
```bash
# Weather MCP Server 및 Client 테스트
PYTHONPATH=. python examples/test_weather_mcp.py
```

#### 🏠 기기 클릭 API 테스트
```bash
# Python 테스트 스크립트
PYTHONPATH=. python examples/test_device_click.py

# 또는 curl 명령어로 직접 테스트 (서버 실행 후)
curl -X POST http://localhost:8000/api/gaze/click \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "clicked_device": {
      "device_id": "ac_001",
      "device_type": "air_conditioner",
      "device_name": "거실 에어컨",
      "display_name": "에어컨",
      "capabilities": ["on_off", "temperature"],
      "current_state": {"is_on": false, "temperature": 24}
    }
  }'
```

## 📡 주요 API 엔드포인트

### POST /api/gaze/click
하드웨어에서 클릭된 IoT 기기 정보를 전송하여 AI 추천을 받습니다.

**요청 예시:**
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "clicked_device": {
    "device_id": "device_002",
    "device_type": "air_conditioner",
    "device_name": "거실 에어컨",
    "display_name": "에어컨",
    "capabilities": ["on_off", "temperature", "mode"],
    "current_state": {
      "is_on": false,
      "temperature": 24
    }
  }
}
```

**응답 예시:**
```json
{
  "status": "success",
  "message": "에어컨 클릭 처리 완료",
  "session_id": "session_456",
  "clicked_device_id": "device_002",
  "recommendation": {
    "intent": "turn_on_ac",
    "confidence": 0.92,
    "prompt_text": "현재 오후 2시입니다. 에어컨을 시원하게 켜시겠습니까?",
    "action": {
      "device_id": "device_002",
      "command": "turn_on",
      "parameters": {
        "temperature": 22,
        "mode": "cool"
      }
    },
    "reasoning": "오후 시간대이고 에어컨이 꺼진 상태이므로 냉방 모드로 켜는 것을 추천"
  }
}
```

더 많은 예시는 [`examples/device_click_examples.json`](examples/device_click_examples.json)을 참조하세요.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해 주세요.