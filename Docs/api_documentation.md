# GazeHome AI Services API Documentation

## 개요

GazeHome AI Services는 시선 추적으로 스마트 홈을 제어하는 AI 에이전트 시스템의 백엔드 API입니다. 라즈베리파이에서 사용자가 시선으로 클릭한 IoT 기기 정보를 받아, LLM Agent를 통해 심층적 의도를 추론하고 최적의 다음 명령어를 추천합니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **인증**: 현재 미구현 (향후 JWT 토큰 기반 인증 예정)

## 데이터 모델

### 기기 클릭 이벤트 구조

#### GazeClickRequest
라즈베리파이에서 전송하는 기기 클릭 요청 (사용자가 시선으로 클릭한 IoT 기기 정보)

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
      "temperature": 24,
      "mode": "cool"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "context": {
    "screen_width": 1920,
    "screen_height": 1080,
    "browser": "chrome"
  }
}
```

#### GazeClickResponse
기기 클릭 처리 응답 (LLM Agent가 생성한 추천 포함)

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
        "mode": "cool",
        "fan_speed": "auto"
      }
    },
    "reasoning": "오후 시간대이고 에어컨이 꺼진 상태이므로 냉방 모드로 켜는 것을 추천"
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

### 스마트 기기 구조

#### SmartDevice
```json
{
  "id": "uuid",
  "user_id": "string",
  "device_id": "device_001",
  "device_type": "light",
  "name": "거실 조명",
  "display_name": "조명",
  "capabilities": ["on_off", "brightness", "color"],
  "current_state": {
    "is_on": true,
    "brightness": 75,
    "color": "#ffffff"
  },
  "ui_position": {"row": 0, "col": 0},
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## API 엔드포인트

### 1. 기기 클릭 이벤트 처리 (주요 엔드포인트)

#### POST /gaze/click
하드웨어에서 사용자가 시선으로 클릭한 IoT 기기 정보를 전송하면, LLM Agent가 의도를 추론하고 최적의 명령어를 추천합니다.

**요청:**
```bash
POST /api/gaze/click
Content-Type: application/json

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
      "temperature": 24,
      "mode": "cool"
    }
  },
  "timestamp": "2024-01-15T14:30:00Z",
  "context": {
    "location": "living_room",
    "weather": "hot"
  }
}
```

**응답:**
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
        "mode": "cool",
        "fan_speed": "auto"
      }
    },
    "reasoning": "오후 시간대이고 에어컨이 꺼진 상태이므로 냉방 모드로 켜는 것을 추천"
  },
  "timestamp": "2024-01-15T14:30:01Z"
}
```

**주요 기능:**
- 클릭된 기기의 현재 상태 분석
- 시간대별 사용 패턴 고려
- 사용자 의도 심층 추론
- 최적의 명령어 및 파라미터 추천
- 친근한 한국어 메시지 생성

#### GET /gaze/status
시선 추적 시스템 상태 확인

**요청:**
```bash
GET /api/gaze/status
```

**응답:**
```json
{
  "status": "active",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "시선 클릭 기반 IoT 제어 시스템 정상 작동 중",
  "mode": "device_click"
}
```

### 2. 메인 제어 페이지

#### GET /main_control_devices
메인 제어 페이지에 표시할 스마트 기기 목록과 상태 조회

**요청:**
```bash
GET /api/main_control_devices?user_id=user_123
```

**응답:**
```json
{
  "status": "success",
  "devices": [
    {
      "device_id": "device_001",
      "device_type": "light",
      "display_name": "조명",
      "current_state": {
        "is_on": true,
        "brightness": 75
      },
      "ui_position": {"row": 0, "col": 0}
    },
    {
      "device_id": "device_002",
      "device_type": "air_conditioner",
      "display_name": "에어컨",
      "current_state": {
        "is_on": false,
        "temperature": 24
      },
      "ui_position": {"row": 0, "col": 1}
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. AI 추천

#### GET /ai_recommendation
AI 기반 추천 페이지에 표시할 추천 내용 조회

**요청:**
```bash
GET /api/ai_recommendation?user_id=user_123&session_id=session_456
```

**응답:**
```json
{
  "status": "success",
  "recommendation": {
    "id": "rec_789",
    "prompt_text": "현재 폭우주의보가 발생했습니다. 에어컨을 제습 모드로 작동하시겠습니까?",
    "action": {
      "device_id": "device_002",
      "command": "turn_on",
      "parameters": {
        "mode": "dehumidify",
        "temperature": 26
      }
    },
    "contextual_insights": [
      {
        "type": "weather",
        "description": "폭우주의보 발효 중",
        "impact_level": "high"
      }
    ],
    "confidence": 0.92
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST /accept_recommendation
사용자가 추천을 수락했을 때의 피드백 수집

**요청:**
```bash
POST /api/accept_recommendation
Content-Type: application/json

{
  "recommendation_id": "rec_789",
  "user_id": "user_123",
  "session_id": "session_456",
  "final_action": {
    "device_id": "device_002",
    "command": "turn_on",
    "parameters": {
      "mode": "dehumidify",
      "temperature": 26
    }
  },
  "reasoning": "날씨가 습해서 에어컨 제습 모드가 필요함"
}
```

**응답:**
```json
{
  "status": "success",
  "message": "추천 수락 피드백 저장 완료",
  "feedback_id": "feedback_123",
  "timestamp": "2024-01-15T10:30:05Z"
}
```

#### POST /reject_recommendation
사용자가 추천을 거부했을 때의 피드백 수집

**요청:**
```bash
POST /api/reject_recommendation
Content-Type: application/json

{
  "recommendation_id": "rec_789",
  "user_id": "user_123",
  "session_id": "session_456",
  "reasoning": "지금은 에어컨이 필요하지 않음"
}
```

**응답:**
```json
{
  "status": "success",
  "message": "추천 거부 피드백 저장 완료",
  "feedback_id": "feedback_124",
  "timestamp": "2024-01-15T10:30:05Z"
}
```

### 4. 개인 맞춤 설정

#### GET /personalized_settings
개인 맞춤 페이지에 표시할 AI 맞춤 추천 및 설정 정보 조회

**요청:**
```bash
GET /api/personalized_settings?user_id=user_123
```

**응답:**
```json
{
  "status": "success",
  "user_preferences": {
    "automation_rules": [
      {
        "rule_id": "rule_001",
        "title": "시각별 미세먼지 알림",
        "description": "미세먼지 농도에 따른 공기청정기 자동 제어",
        "is_active": true
      }
    ],
    "time_patterns": {
      "evening_lights": "18:00-22:00",
      "morning_ac": "07:00-09:00"
    }
  },
  "ai_recommendations": [
    {
      "type": "automation",
      "title": "나만의 영화 시청 모드",
      "description": "조명 어둡게, TV 켜기, 사운드바 연결",
      "confidence": 0.85
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 5. 스마트 기기 관리

#### GET /devices
사용자의 모든 스마트 기기 조회

**요청:**
```bash
GET /api/devices?user_id=user_123
```

**응답:**
```json
{
  "status": "success",
  "devices": [
    {
      "id": "uuid_001",
      "device_id": "device_001",
      "device_type": "light",
      "name": "거실 조명",
      "display_name": "조명",
      "capabilities": ["on_off", "brightness", "color"],
      "current_state": {
        "is_on": true,
        "brightness": 75,
        "color": "#ffffff"
      },
      "is_active": true
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST /devices
새 스마트 기기 추가

**요청:**
```bash
POST /api/devices
Content-Type: application/json

{
  "user_id": "user_123",
  "device_id": "device_005",
  "device_type": "speaker",
  "name": "거실 스피커",
  "display_name": "스피커",
  "capabilities": ["on_off", "volume"],
  "ui_position": {"row": 1, "col": 0}
}
```

**응답:**
```json
{
  "status": "success",
  "message": "스마트 기기 추가 완료",
  "device_id": "device_005",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### PUT /devices/{device_id}
스마트 기기 정보 수정

**요청:**
```bash
PUT /api/devices/device_001
Content-Type: application/json

{
  "name": "거실 메인 조명",
  "display_name": "메인 조명",
  "capabilities": ["on_off", "brightness", "color", "timer"]
}
```

**응답:**
```json
{
  "status": "success",
  "message": "스마트 기기 정보 수정 완료",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### DELETE /devices/{device_id}
스마트 기기 삭제 (비활성화)

**요청:**
```bash
DELETE /api/devices/device_001?user_id=user_123
```

**응답:**
```json
{
  "status": "success",
  "message": "스마트 기기 삭제 완료",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 에러 응답

모든 API는 다음과 같은 에러 응답 형식을 사용합니다:

```json
{
  "status": "error",
  "message": "에러 메시지",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "추가 에러 정보"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 일반적인 에러 코드

- `INVALID_REQUEST`: 잘못된 요청 형식
- `USER_NOT_FOUND`: 사용자를 찾을 수 없음
- `DEVICE_NOT_FOUND`: 기기를 찾을 수 없음
- `SESSION_EXPIRED`: 세션이 만료됨
- `AGENT_ERROR`: AI 에이전트 처리 중 오류
- `DATABASE_ERROR`: 데이터베이스 오류
- `EXTERNAL_API_ERROR`: 외부 API 호출 오류

## 테스트 및 개발 가이드

### 하드웨어 팀을 위한 테스트 예시

#### 예시 1: 에어컨 클릭
```bash
curl -X POST http://localhost:8000/api/gaze/click \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "session_id": "session_456",
    "clicked_device": {
      "device_id": "ac_001",
      "device_type": "air_conditioner",
      "device_name": "거실 에어컨",
      "display_name": "에어컨",
      "capabilities": ["on_off", "temperature", "mode"],
      "current_state": {
        "is_on": false,
        "temperature": 24
      }
    }
  }'
```

#### 예시 2: 조명 클릭
```bash
curl -X POST http://localhost:8000/api/gaze/click \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "session_id": "session_789",
    "clicked_device": {
      "device_id": "light_001",
      "device_type": "light",
      "device_name": "거실 조명",
      "display_name": "조명",
      "capabilities": ["on_off", "brightness", "color"],
      "current_state": {
        "is_on": true,
        "brightness": 80
      }
    }
  }'
```

#### Python 테스트 스크립트
```bash
# 테스트 스크립트 실행
python examples/test_device_click.py
```

더 많은 예시는 `examples/device_click_examples.json` 파일을 참조하세요.

---

## 확장성 고려사항

### 1. 새로운 기기 타입 추가

새로운 스마트 기기 타입을 추가할 때는 다음과 같이 처리됩니다:

1. **기기 타입 등록**: `DeviceType` enum에 새 타입 추가
2. **기능 정의**: `DeviceCapability` enum에 새 기능 추가
3. **자동 인식**: 라즈베리파이에서 `device_mapping`에 새 기기 정보 포함
4. **에이전트 학습**: AI 에이전트가 새 기기 타입의 의도를 자동 학습

### 2. 동적 UI 레이아웃

- 사용자별로 다른 기기 구성을 가질 수 있음
- 여러 레이아웃 프로필 지원 (거실, 침실, 사무실 등)
- 런타임에 기기 추가/제거 가능


## 보안 고려사항

### 1. 데이터 보호
- 사용자 시선 데이터 암호화 저장
- 개인정보 보존 기간 정책 (기본 30일)
- 접근 로그 기록

### 2. API 보안
- 향후 JWT 토큰 기반 인증 구현 예정
- Rate Limiting 적용 예정
- CORS 설정으로 허용된 도메인만 접근 가능

## 성능 최적화

### 1. 캐싱 전략
- 사용자 기기 정보 캐싱
- 환경 데이터 캐싱
- AI 추천 결과 캐싱

### 2. 비동기 처리
- 모든 I/O 작업 비동기 처리
- 에이전트 병렬 실행
- 배치 처리 지원

이 API 문서는 GazeHome AI Services의 현재 구현 상태를 반영하며, 개발 과정에서 지속적으로 업데이트될 예정입니다.
