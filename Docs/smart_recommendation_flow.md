# GazeHome AI Services - 스마트 추천 플로우

## 📋 개요

GazeHome AI Services의 상태 기반 스마트 추천 시스템의 상세한 작동 방식을 설명합니다.

## 🎯 핵심 개념

### 상태 기반 스마트 추천
- **기존**: 기기 목록만 조회하여 추천
- **개선**: 각 기기의 실시간 상태를 확인하여 더 스마트한 추천 생성

## 🔄 상세 추천 플로우

### 1단계: 기기 목록 및 상태 조회

```python
# Gateway에서 등록된 기기 목록 조회
gateway_devices = await gateway_client.get_available_devices()
available_devices = gateway_devices.get('response', [])

# 각 기기의 상태를 개별적으로 확인
for device in available_devices:
    device_id = device['deviceId']
    device_status = await self._check_device_status(device_id)
```

**결과 예시:**
```json
{
  "device_id": "에어컨1_ID",
  "is_online": true,
  "current_state": "RUNNING",
  "is_running": true,
  "can_control": true
}
```

### 2단계: AI에게 상태 정보 제공

```
=== 등록된 기기 목록 ===
- 에어컨1 (DEVICE_AIR_CONDITIONER) - 상태: 실행중, 제어가능
- 공기청정기 (DEVICE_AIR_PURIFIER) - 상태: 정지중, 제어가능
- 건조기 (DEVICE_DRYER) - 상태: 정지중, 제어불가
```

### 3단계: AI가 상태를 고려한 추천 생성

AI가 기기 상태를 분석하여 추천:

- **에어컨1**: 이미 실행중 → "에어컨 끌까요?" 추천
- **공기청정기**: 정지중 → "공기청정기 켤까요?" 추천  
- **건조기**: 제어불가 → 추천하지 않음

### 4단계: 스마트 액션 결정

```python
def _determine_smart_action(original_action, device_status):
    # 이미 실행 중인 기기를 켜려고 하면 끄기로 변경
    if original_action == "turn_on" and device_status["is_running"]:
        return "turn_off"
    
    # 이미 꺼진 기기를 끄려고 하면 켜기로 변경
    if original_action == "turn_off" and not device_status["is_running"]:
        return "turn_on"
    
    # 그 외의 경우 원래 액션 유지
    return original_action
```

### 5단계: 제어 실행

```python
# 최종 제어 정보
{
    "device_id": "에어컨1_ID",
    "action": "turn_off",  # 스마트 액션으로 변경됨
    "device_alias": "에어컨1",
    "device_status": {
        "is_running": true,
        "current_state": "RUNNING",
        "can_control": true
    }
}
```

## 📊 플로우 다이어그램

```
사용자 요청/스케줄러 트리거
         ↓
1. Gateway에서 기기 목록 조회
         ↓
2. 각 기기별 상태 확인 (get_device_profile)
         ↓
3. AI에게 기기 목록 + 상태 정보 제공
         ↓
4. AI가 상태를 고려한 추천 생성
         ↓
5. 스마트 액션 결정 (이미 켜진 기기 → 끄기)
         ↓
6. 사용자에게 추천 전송
         ↓
7. 사용자 YES → 실제 제어 실행
```

## 🔍 핵심 개선사항

### Before (기존 방식)
```
기기 목록만 조회 → AI 추천 → 제어 실행
(상태 무시)
```

### After (개선된 방식)
```
기기 목록 조회 → 각 기기 상태 확인 → AI에게 상태 정보 제공 
→ 상태 기반 추천 → 스마트 액션 결정 → 제어 실행
```

## 💡 실제 시나리오 예시

### 시나리오: 아침 7시, 에어컨이 이미 켜져있음

#### 1. 기기 상태 확인
- **에어컨1**: 실행중, 제어가능
- **공기청정기**: 정지중, 제어가능

#### 2. AI 추천 생성
- "에어컨 끌까요?" (이미 켜져있으니 끄기 추천)
- "공기청정기 켤까요?" (정지중이니 켜기 추천)

#### 3. 스마트 액션 결정
- **에어컨1**: `turn_on` → `turn_off` (이미 켜져있으니 끄기)
- **공기청정기**: `turn_on` (정지중이니 켜기)

#### 4. 최종 결과
- 사용자에게 "에어컨 끌까요?" 추천
- 사용자 YES → 에어컨 끄기 실행

## 🛠️ 기술적 구현

### 주요 함수들

#### `_check_device_status(device_id)`
- Gateway API를 통해 기기 상태 조회
- `runState`, `remoteControlEnable` 등 상태 정보 추출
- 오류 처리 및 안전한 기본값 반환

#### `_determine_smart_action(original_action, device_status)`
- 기기 상태에 따른 스마트 액션 결정
- 이미 실행중/정지중인 기기에 대한 로직 처리

#### `_prepare_device_control_from_ai(device_control_info)`
- AI 추천 정보를 실제 제어 명령으로 변환
- 기기 상태 확인 및 스마트 액션 적용

## 🎯 장점

1. **정확한 상태 파악**: 실시간 기기 상태 확인
2. **스마트한 추천**: 상태를 고려한 적절한 추천
3. **사용자 경험 향상**: 이미 켜진 기기를 또 켜려고 하지 않음
4. **에너지 효율성**: 불필요한 제어 방지
5. **오류 방지**: 제어 불가능한 기기 추천 방지

## 📝 로그 예시

```
🔍 기기 상태 확인: 에어컨1_ID -> RUNNING (실행중: True)
🔄 스마트 액션: 이미 실행 중이므로 끄기로 변경
✅ AI 제어 정보로 기기 찾기 완료: 에어컨1 -> turn_off
🎯 기기 상태: RUNNING (실행중: True)
```

## 🔧 설정 및 환경

### 필요한 API 엔드포인트
- `GET /api/lg/devices` - 기기 목록 조회
- `GET /api/lg/devices/{device_id}/profile` - 기기 상태 조회
- `POST /api/lg/control` - 기기 제어 실행

### 환경 변수
- `GATEWAY_URL`: Gateway 서버 URL
- `GATEWAY_CONTROL_ENDPOINT`: 제어 API 엔드포인트
- `GATEWAY_DEVICES_ENDPOINT`: 기기 목록 API 엔드포인트

---

**이 문서는 GazeHome AI Services의 상태 기반 스마트 추천 시스템의 작동 방식을 설명합니다.**

