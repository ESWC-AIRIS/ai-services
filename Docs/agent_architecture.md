# GazeHome AI Agent Architecture

## 개요

GazeHome의 AI 에이전트 시스템은 사용자의 시선 추적 데이터와 외부 환경 정보를 종합적으로 분석하여 지능적인 스마트 홈 제어를 제공하는 시스템입니다.

> 🎯 **현재 상태 (MVP)**: **Single Agent 아키텍처**  
> 현재는 `LLMService`가 **하나의 통합 Agent**로 작동하며, 의도 추론, 상황 분석, 추천 생성을 모두 처리합니다.  
> 이는 빠른 응답 속도와 단순한 구조를 위한 MVP 전략입니다.

> 🔮 **미래 확장**: **Multi-Agent 아키텍처**  
> 필요에 따라 3단계 에이전트 구조(Intent Recognition → Context Analysis → Recommendation)로 확장 가능하도록 설계되었습니다.

> ⚠️ **2025-10-08 업데이트**: 시스템이 클릭 기반으로 전환되면서 **Agent 1의 역할이 크게 축소**되었습니다.  
> 하드웨어에서 이미 클릭된 기기 정보를 제공하므로, "어떤 기기를 제어하려는지" 파악하는 기능은 더 이상 필요하지 않습니다.

## 시스템 아키텍처

### 현재 구조도 (Single Agent - MVP)

```
하드웨어 (클릭 이벤트)
    ↓ HTTP POST /api/gaze/click
FastAPI Server
    ↓
LLMService (Single Agent)
├── Perception: 기기 정보, 시간, 컨텍스트 수집
├── MCP Integration: 날씨 API 등 외부 정보
├── Reasoning: Gemini LLM 기반 통합 추론
│   ├── 의도 파악 (Intent Recognition)
│   ├── 상황 분석 (Context Analysis)
│   └── 추천 생성 (Recommendation)
└── Action: 최적 명령어 및 파라미터 결정
    ↓
추천 결과 반환 (JSON)
```

### 미래 확장 구조도 (Multi-Agent System)

```
UI Layer (React/Vue)
    ↓ HTTP Requests
FastAPI Server
    ↓ Agent Coordination
Agent System
├── Agent 1: Intent Recognition Agent
├── Agent 2: Contextual Analysis Agent
└── Agent 3: Recommendation Agent
    ↓ External APIs
External Services (Weather, Air Quality, etc.)
    ↓ Feedback Loop
Learning & Adaptation System
```

## 에이전트별 역할 및 기능

### 현재: Single Agent (LLMService)

> 🎯 **현재 구현**: `app/services/llm_service.py`의 `LLMService` 클래스가 **하나의 통합 Agent**로 작동합니다.

**Agent의 구성 요소**:
```python
class LLMService:  # Single Agent
    
    # 1. Perception (환경 인식)
    async def generate_device_recommendation(device_info, context):
        - 클릭된 기기 정보 수신
        - 현재 시간 및 컨텍스트 파악
        - MCP를 통한 날씨 정보 조회
    
    # 2. Reasoning (추론)
        - Gemini LLM 기반 통합 추론
        - 의도 파악 + 상황 분석 + 추천 생성
    
    # 3. Action (행동 결정)
        - 최적 명령어 결정
        - 파라미터 설정
        - 사용자 안내 메시지 생성
```

**장점**:
- ✅ 빠른 응답 속도 (단일 LLM 호출)
- ✅ 간단한 구조 (에이전트 간 조율 불필요)
- ✅ 유지보수 용이
- ✅ MVP에 적합

**한계**:
- ⚠️ 복잡한 다단계 추론 제한
- ⚠️ 전문화된 처리 어려움
- ⚠️ 병렬 처리 불가

---

### 미래: Multi-Agent System

### Agent 1: 의도 파악 에이전트 (Intent Recognition Agent) ~~[현재는 통합됨]~~

> 🔄 **현재 상태**: 클릭 기반 시스템으로 전환되면서 이 에이전트의 주요 기능이 **LLMService로 통합**되었습니다.

**기존 목표** ~~(더 이상 필요 없음)~~: 
- ~~사용자 시선 데이터와 행동 패턴을 분석하여 명시적/묵시적 의도를 파악~~
- ~~시선-의도 매핑: 특정 기기에 대한 응시가 일정 시간 이상 지속될 경우 제어 의도로 간주~~

**변경 이유**:
- **이전**: x,y 좌표 → Agent 1이 "어떤 기기를 보는지" 판단 필요
- **현재**: 하드웨어가 이미 "어떤 기기를 클릭했는지" 전송 → **판단 불필요**
- **의도 추론**: 이제 `LLMService.generate_device_recommendation()`에서 처리

**현재 통합된 기능** (`app/services/llm_service.py`):
```python
async def generate_device_recommendation(device_info, context):
    """
    - 클릭된 기기 정보 직접 수신
    - 기기 상태, 시간대, 사용자 컨텍스트 분석
    - 의도 추론 + 추천 생성을 한 번에 처리
    """
```

**입력 데이터** (현재):
- ✅ `clicked_device`: 하드웨어가 제공한 클릭된 기기 정보
- ✅ `current_state`: 기기의 현재 상태 (켜짐/꺼짐 등)
- ✅ `time_context`: 시간대 정보

**출력 데이터** (현재):
- ✅ `intent`: 추론된 사용자 의도
- ✅ `confidence`: 신뢰도
- ✅ `prompt_text`: 사용자에게 보여줄 추천 메시지
- ✅ `action`: 실행할 명령어

> 💡 **결론**: Agent 1의 역할은 더 이상 독립적으로 필요하지 않으며, LLM 서비스에 통합되었습니다.

### Agent 2: 상황 분석 에이전트 (Contextual Analysis Agent)

**목표**: 의도 파악 에이전트의 출력과 실시간 외부 환경 데이터를 결합하여 맥락적 정보 제공

**주요 기능**:
- 규칙 기반 시나리오 매칭: 특정 외부 환경 조건과 사용자 의도를 결합하여 추천 시나리오 식별
- 최적의 맥락 생성: 환경 조건에 맞춰 적정 제어 파라미터 제안
- 실시간 환경 모니터링: 날씨, 대기질, 시간대 등 외부 요인 지속적 분석

**입력 데이터**:
- `potential_intent`: 의도 파악 에이전트의 출력
- `weather_data`: 현재 날씨, 폭우/폭염주의보, 기온, 습도
- `air_quality_data`: 미세먼지(PM2.5, PM10) 농도
- `time_data`: 현재 시각, 요일, 일출/일몰 시간
- `calendar_data`: 사용자의 개인 일정 (선택 사항)

**출력 데이터**:
- `contextual_insights`: '폭우', '고온다습', '미세먼지 나쁨', '일몰 후' 등 현재 상황 요약
- `recommendation_scenario`: '폭우시 에어컨 제안', '미세먼지시 공기청정기 제안'
- `suggested_parameters`: '온도 24도', '습도 50%', '밝기 70%' 등 구체적인 제어 값

**UI 연동**:
- AI 기반 추천 페이지에 "현재 폭우주의보가 발생했습니다. 에어컨을 작동하시겠습니까?" 같은 사전 제안의 근거 생성
- 개인 맞춤 페이지에 "미세먼지 농도 상승을 감지하여 공기청정기를 강하게 제어" 같은 자동화 규칙 추천 정보 제공

### Agent 3: 추천 에이전트 (Recommendation Agent)

**목표**: 상황 분석 에이전트의 결과와 사용자 개인 설정, 과거 선호도를 바탕으로 최종 제안 생성

**주요 기능**:
- 사용자 선호도 매칭: 상황별로 어떤 명령을 가장 선호했는지 과거 데이터 분석
- 프롬프트 생성: UI에 바로 표시될 수 있도록 자연어 형태로 추천 문구 생성
- 자동화 규칙 제안: 사용자의 생활 패턴과 외부 환경 분석을 통해 새로운 자동화 규칙 제안

**입력 데이터**:
- `contextual_insights`, `recommendation_scenario`, `suggested_parameters`: 상황 분석 에이전트의 출력
- `user_personalized_settings`: 사용자가 이전에 설정한 자동화 규칙, 선호하는 기기 모드
- `user_feedback_history`: 과거 추천 수락/거부 이력

**출력 데이터**:
- `prompt_text`: "현재 폭우주의보가 발생했습니다. 에어컨을 작동하시겠습니까?"
- `action_to_recommend`: {'device_id': 'ac_01', 'command': 'turn_on', 'mode': 'dehumidify', 'temp': 24}
- `personalized_recommendation_list`: 개인화된 자동화 규칙 및 장면 제안

**UI 연동**:
- AI 기반 추천 페이지에 표시될 최종 문구 생성 및 "네, 해주세요" / "아니오, 괜찮습니다" 선택지에 대한 액션 정의
- 개인 맞춤 페이지의 "AI 맞춤형 스마트 홈 추천" 섹션에 표시될 개인화된 자동화 규칙 제안

## API 엔드포인트 설계

### 기존 엔드포인트 확장

```
POST /api/gaze/track → POST /gaze_data
GET /api/devices/ → GET /main_control_devices
```

### 새로 추가할 엔드포인트

```
GET /ai_recommendation
- AI 기반 추천 페이지에 표시할 추천 내용 제공
- Response: 추천 문구, 액션, 선택지

POST /accept_recommendation
- 사용자가 추천을 수락했을 때의 피드백 수집
- Request: 추천 ID, 수락 시간, 최종 실행된 액션

POST /reject_recommendation  
- 사용자가 추천을 거부했을 때의 피드백 수집
- Request: 추천 ID, 거부 시간, 거부 사유

GET /personalized_settings
- 개인 맞춤 페이지에 표시할 AI 맞춤 추천 및 설정 정보 제공
- Response: 자동화 규칙 목록, 개인화 추천, 설정 옵션
```

## Gemini API 연동

### LLM 기반 에이전트 시스템

모든 에이전트는 Google Gemini API를 활용하여 구현되며, 각 에이전트별로 특화된 프롬프트와 컨텍스트를 제공합니다.

**Gemini API 활용 방식**:
- **의도 파악 에이전트**: 시선 데이터와 사용자 패턴을 자연어로 변환하여 의도 분석
- **상황 분석 에이전트**: 외부 환경 데이터를 맥락적으로 해석하고 시나리오 생성
- **추천 에이전트**: 사용자 선호도와 상황을 종합하여 개인화된 추천 생성

**프롬프트 엔지니어링**:
- 각 에이전트별로 특화된 시스템 프롬프트 설계
- 컨텍스트 정보를 구조화된 형태로 전달
- 응답 형식을 JSON으로 표준화하여 파싱 효율성 향상

## 피드백 및 학습 시스템

### 명시적 피드백 수집

1. **추천 수락/거부 버튼**: 사용자의 직접적인 피드백 수집
2. **개인 맞춤 페이지 설정 변경**: AI 추천 설정 수정/추가 행위
3. **기기 제어 결과**: 최종 실행된 액션의 성공/실패 여부

### 학습 루프

1. **데이터 저장**: 모든 피드백 데이터를 데이터베이스에 저장
2. **주기적 재학습**: 누적된 피드백 데이터를 활용하여 각 에이전트의 머신러닝 모델 재학습
3. **모델 업데이트**: 사용자 선호도 변화를 빠르게 반영하도록 모델 개선

## 시스템 통합 및 테스트

### 에이전트 간 데이터 흐름
1. **시선 데이터 수신** → 의도 파악 에이전트 (Gemini API 호출)
2. **의도 분석 결과** → 상황 분석 에이전트 (Gemini API 호출)
3. **맥락 정보** → 추천 에이전트 (Gemini API 호출)
4. **최종 추천** → UI 응답 및 사용자 피드백 수집

### 테스트 시나리오
- **정상 시나리오**: 시선 추적 → 의도 파악 → 상황 분석 → 추천 생성 → 사용자 응답
- **에러 시나리오**: API 장애 시 fallback 메커니즘 테스트
- **성능 테스트**: 다중 에이전트 병렬 처리 성능 측정

## 성능 및 확장성 고려사항

### 성능 최적화
- **병렬 처리**: 에이전트들의 병렬 실행으로 지연 시간 최소화
- **Gemini API 캐싱**: 동일한 컨텍스트에 대한 중복 API 호출 방지
- **비동기 처리**: I/O 집약적 작업의 비동기 처리
- **프롬프트 최적화**: 컨텍스트 길이 최적화로 API 호출 비용 절감

### 확장성 설계
- **모듈화**: 새로운 에이전트 추가 시 기존 코드 영향 최소화
- **API 버전 관리**: 하위 호환성을 위한 API 버전 관리
- **장애 복구**: Gemini API 장애 시 fallback 메커니즘 (로컬 규칙 기반 처리)

### 모니터링 및 로깅
- **에이전트별 성능 메트릭**: Gemini API 응답 시간, 정확도, 사용자 만족도
- **API 사용량 모니터링**: Gemini API 호출 빈도 및 토큰 사용량 추적
- **에러 추적**: 각 에이전트의 실패 원인 분석 및 개선
- **사용자 행동 분석**: UI 상호작용 패턴 분석을 통한 UX 개선

## 보안 및 프라이버시

### 데이터 보호
- **개인정보 암호화**: 사용자 시선 데이터 및 행동 패턴 암호화 저장
- **접근 권한 관리**: 사용자별 데이터 접근 권한 제어
- **데이터 보존 정책**: 개인정보 보존 기간 및 삭제 정책 수립

### AI 모델 보안
- **Gemini API 보안**: API 키 관리 및 접근 제어
- **추천 결과 검증**: Gemini API 응답의 편향성 및 공정성 검증
- **사용자 제어**: AI 추천 시스템의 투명성 및 사용자 제어권 보장
- **악의적 사용 방지**: 시스템 오남용 및 조작 시도 탐지

이 아키텍처 문서는 GazeHome AI 에이전트 시스템의 설계 방향과 구현 계획을 담고 있으며, 개발 과정에서 지속적으로 업데이트될 예정입니다.
