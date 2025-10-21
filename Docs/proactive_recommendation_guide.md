# 능동적 추천 시스템 가이드

## 개요

능동적 추천 시스템은 AI가 적절한 타이밍에 사용자에게 스마트 가전 제어를 추천하는 기능입니다.

## 동작 흐름

```
1. AI가 주기적으로 실행 (30분마다)
   ↓
2. 현재 컨텍스트 분석
   - 시간대 (아침/점심/저녁/밤)
   - 날씨 정보 (온도, 습도, 날씨 상태)
   - 사용자 패턴 (Long-term Memory)
   ↓
3. LLM이 추천 필요 여부 판단
   ↓
4. 추천 문구 생성
   ↓
5. 하드웨어로 추천 전송
   ↓
6. 사용자에게 추천 표시
   ↓
7. 사용자 컨펌 대기
   ↓
8. 수락 시 → 해당 기기 제어 실행
   거부 시 → 피드백 학습
```

## 추천 문구 예시

### 예시 1: 더운 날씨 에어컨 냉방 추천
```json
{
  "should_recommend": true,
  "device_id": "ac_living_room",
  "device_name": "거실 에어컨",
  "confidence": 0.92,
  "prompt_text": "현재 기온이 30도입니다. 에어컨을 켜시겠습니까?",
  "action": {
    "command": "turn_on",
    "parameters": {
      "mode": "cool",
      "temperature": 24
    }
  },
  "reasoning": "현재 외부 기온이 30도로 높고, 에어컨이 꺼져 있어 냉방 모드로 켜기를 추천합니다."
}
```

**사용자에게 표시되는 화면:**
```
❄️ AI 추천
"현재 기온이 30도입니다. 에어컨을 켜시겠습니까?"

[네, 해주세요]  [아니요, 괜찮습니다]
```

### 예시 2: 미세먼지 공기청정기 추천
```json
{
  "should_recommend": true,
  "device_id": "air_purifier_living_room",
  "device_name": "거실 공기청정기",
  "confidence": 0.95,
  "prompt_text": "미세먼지 농도가 높습니다. 공기청정기를 강하게 작동시키시겠습니까?",
  "action": {
    "command": "turn_on",
    "parameters": {
      "mode": "turbo",
      "fan_speed": 3
    }
  },
  "reasoning": "미세먼지 농도가 '나쁨' 수준이므로 공기청정기를 강하게 작동시키기를 추천합니다."
}
```

### 예시 3: 추운 날씨 난방 추천
```json
{
  "should_recommend": true,
  "device_id": "ac_living_room",
  "device_name": "거실 에어컨",
  "confidence": 0.9,
  "prompt_text": "기온이 낮습니다. 에어컨 난방 모드를 켜시겠습니까?",
  "action": {
    "command": "turn_on",
    "parameters": {
      "mode": "heat",
      "temperature": 22
    }
  },
  "reasoning": "현재 외부 기온이 5도로 매우 낮아 난방 모드로 켜기를 추천합니다."
}
```

### 예시 4: 비 오는 날 제습 추천
```json
{
  "should_recommend": true,
  "device_id": "ac_living_room",
  "device_name": "거실 에어컨",
  "confidence": 0.88,
  "prompt_text": "비가 오고 습도가 높습니다. 제습 모드를 켜시겠습니까?",
  "action": {
    "command": "turn_on",
    "parameters": {
      "mode": "dehumidify",
      "temperature": 24
    }
  },
  "reasoning": "비가 오고 습도가 85%로 높아 제습 모드를 추천합니다."
}
```

### 예시 5: 추천하지 않는 경우
```json
{
  "should_recommend": false,
  "reasoning": "현재 모든 기기가 적절하게 작동 중이며, 특별히 변경할 필요가 없습니다."
}
```

## 하드웨어로 전송되는 데이터

### 왜 action 정보도 함께 전송하는가?

**Stateless 설계**를 통해 성능과 확장성을 확보하기 위함입니다:

**장점:**
1. ⚡ **빠른 응답**: AI가 DB에서 추천 내역을 조회할 필요 없이 즉시 기기 제어 가능
2. 🎯 **투명성**: Hardware가 정확한 제어 내용을 사용자에게 표시 가능 (예: "70% 밝기로 켜기")
3. 🔧 **유연성**: Hardware가 사용자 입력에 따라 action을 수정해서 반환 가능
4. 💾 **DB 부하 감소**: 모든 추천을 DB에 저장하지 않아도 됨

**흐름 비교:**

```
❌ Stateful 방식 (recommendation_id만 전송):
Hardware → AI: recommendation_id + accepted
AI: DB에서 recommendation_id로 action 조회 (느림)
AI: action 실행

✅ Stateless 방식 (action 포함):
Hardware → AI: action + accepted  
AI: 받은 action 즉시 실행 (빠름)
```

하드웨어는 다음 형식으로 추천을 받습니다:

```json
{
  "user_id": "user_001",
  "type": "proactive",
  "timestamp": "2025-10-14T19:35:00+09:00",
  "recommendation": {
    "should_recommend": true,
    "device_id": "light_living_room",
    "device_name": "거실 조명",
    "confidence": 0.85,
    "prompt_text": "저녁이 되었습니다. 거실 조명을 켜시겠습니까?",
    "action": {
      "command": "turn_on",
      "parameters": {
        "brightness": 70
      }
    },
    "reasoning": "현재 저녁 시간(18시)이고 조명이 꺼져 있어 켜기를 추천합니다."
  }
}
```

## 하드웨어 구현 가이드

### 1. 추천 수신 엔드포인트 구현

하드웨어는 다음 엔드포인트를 구현해야 합니다:

```
POST http://localhost:8080/api/recommendations
```

**요청 본문:**
```json
{
  "user_id": "user_001",
  "type": "proactive",
  "recommendation": { ... }
}
```

**응답:**
```json
{
  "status": "success",
  "message": "추천 수신 완료"
}
```

### 2. 사용자에게 추천 표시

```javascript
// 추천 수신 예시 (하드웨어 측)
app.post('/api/recommendations', async (req, res) => {
  const { user_id, recommendation } = req.body;
  
  if (recommendation.should_recommend) {
    // action 정보를 활용하여 상세한 추천 표시
    const actionDetails = formatActionDetails(recommendation.action);
    
    // 사용자에게 추천 문구 표시
    const userResponse = await showRecommendationToUser({
      message: recommendation.prompt_text,
      deviceName: recommendation.device_name,
      actionDetails: actionDetails  // 예: "밝기 70%로 켜기"
    });
    
    // 사용자 응답을 AI로 전송 (action 정보 포함)
    await sendResponseToAI(user_id, recommendation, userResponse);
  }
  
  res.json({ status: 'success' });
});

// action을 사용자 친화적 문구로 변환
function formatActionDetails(action) {
  const { command, parameters } = action;
  
  if (command === 'turn_on' && parameters.brightness) {
    return `밝기 ${parameters.brightness}%로 켜기`;
  } else if (command === 'set_temperature' && parameters.temperature) {
    return `온도 ${parameters.temperature}°C로 설정`;
  }
  // ... 기타 명령어
  return command;
}
```

### 3. 사용자 응답 처리

**중요**: AI가 기기를 제어하므로, Hardware는 **action 정보를 그대로 AI에 돌려주기만** 하면 됩니다.

```javascript
async function sendResponseToAI(user_id, recommendation, accepted) {
  // action 정보를 그대로 AI에 전송 (Stateless 설계)
  await fetch('http://localhost:8000/api/recommendations/response', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: user_id,
      accepted: accepted,  // true or false
      device_id: recommendation.device_id,
      action: recommendation.action  // ← 받은 action을 그대로 반환
    })
  });
  
  // AI가 알아서:
  // - accepted=true이면 → 기기 제어 실행 + 긍정 피드백 학습
  // - accepted=false이면 → 부정 피드백 학습
}

// 사용자가 "네, 해주세요" 클릭
function onAcceptRecommendation(recommendation) {
  sendResponseToAI(user_id, recommendation, true);
}

// 사용자가 "아니요, 괜찮습니다" 클릭
function onRejectRecommendation(recommendation) {
  sendResponseToAI(user_id, recommendation, false);
}
```

**선택 사항**: Hardware가 사용자 설정을 반영하여 action을 수정할 수도 있습니다.

```javascript
// 예: 사용자가 밝기를 조정한 경우
function onAcceptWithCustomBrightness(recommendation, userBrightness) {
  const modifiedAction = {
    ...recommendation.action,
    parameters: {
      ...recommendation.action.parameters,
      brightness: userBrightness  // 사용자가 조정한 값
    }
  };
  
  await fetch('http://localhost:8000/api/recommendations/response', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: user_id,
      accepted: true,
      device_id: recommendation.device_id,
      action: modifiedAction  // ← 수정된 action 전송
    })
  });
}
```

## 로그 예시

서버가 실행되면 다음과 같은 로그를 볼 수 있습니다:

```
2025-10-14 19:35:02 [KST] app.core.scheduler - INFO - === 능동적 추천 작업 시작 ===
2025-10-14 19:35:02 [KST] app.core.scheduler - INFO - 활성 사용자 수: 2

2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO - 📢 추천 생성됨:
2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO -   - 기기: 거실 조명 (light_living_room)
2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO -   - 추천 문구: "저녁이 되었습니다. 거실 조명을 켜시겠습니까?"
2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO -   - 명령어: turn_on
2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO -   - 이유: 현재 저녁 시간(18시)이고 조명이 꺼져 있어 켜기를 추천합니다.
2025-10-14 19:35:05 [KST] app.services.proactive_recommendation_service - INFO -   - 신뢰도: 0.85

2025-10-14 19:35:05 [KST] app.services.hardware_client - INFO - 🚀 하드웨어로 추천 전송 시작:
2025-10-14 19:35:05 [KST] app.services.hardware_client - INFO -   - 사용자: user_001
2025-10-14 19:35:05 [KST] app.services.hardware_client - INFO -   - 추천 문구: "저녁이 되었습니다. 거실 조명을 켜시겠습니까?"
2025-10-14 19:35:05 [KST] app.services.hardware_client - INFO -   - 기기: 거실 조명 (light_living_room)
2025-10-14 19:35:05 [KST] app.services.hardware_client - INFO -   - 명령어: {'command': 'turn_on', 'parameters': {'brightness': 70}}

2025-10-14 19:35:08 [KST] app.services.hardware_client - INFO - ✅ 추천 전송 성공: user_id=user_001
2025-10-14 19:35:13 [KST] app.core.scheduler - INFO - === 능동적 추천 작업 완료 === 성공: 1, 실패: 0, 소요시간: 11.2초
```

## 테스트 방법

### 1. 스케줄러 상태 확인
```bash
curl http://localhost:8000/api/scheduler/status
```

**응답:**
```json
{
  "is_running": true,
  "is_enabled": true,
  "interval_minutes": 30,
  "jobs": [
    {
      "id": "proactive_recommendation_job",
      "name": "능동적 추천 생성 및 전송",
      "next_run_time": "2025-10-14T20:05:00+09:00"
    }
  ],
  "timezone": "Asia/Seoul"
}
```

### 2. 즉시 추천 실행 (테스트용)
```bash
curl -X POST http://localhost:8000/api/scheduler/trigger
```

30분을 기다리지 않고 즉시 추천을 생성하고 전송합니다.

## 설정

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

```env
# 능동적 추천 활성화/비활성화
PROACTIVE_RECOMMENDATION_ENABLED=true

# 추천 주기 (분 단위, 기본 30분)
PROACTIVE_RECOMMENDATION_INTERVAL_MINUTES=30

# 하드웨어 엔드포인트
HARDWARE_ENDPOINT=http://localhost:8080/api/recommendations
```

## FAQ

### Q: 추천이 너무 자주 오는데 어떻게 조절하나요?
A: `.env` 파일에서 `PROACTIVE_RECOMMENDATION_INTERVAL_MINUTES` 값을 늘리세요. (예: 60 = 1시간마다)

### Q: 특정 기기는 추천에서 제외하고 싶어요
A: 현재는 LLM이 모든 기기를 고려하지만, 향후 사용자 설정에서 제외 기기를 설정할 수 있도록 구현 예정입니다.

### Q: 사용자가 거부한 추천은 학습되나요?
A: 현재는 피드백 수집 기능이 구현되지 않았습니다. Phase 2에서 피드백 학습 기능이 추가될 예정입니다.

### Q: MongoDB 없이도 작동하나요?
A: 네, MongoDB 없이도 기본 추천 기능은 작동합니다. 단, 추천 이력 저장과 Long-term Memory 기능이 제한됩니다.

