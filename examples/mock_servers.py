"""
GazeHome AI Services - Mock 서버들
테스트를 위한 Mock 하드웨어 및 Gateway 서버

실행 방법:
    PYTHONPATH=. python examples/mock_servers.py
"""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import logging
from datetime import datetime
import pytz

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

# Mock 하드웨어 서버
hardware_app = FastAPI(title="Mock Hardware Server", version="1.0.0")

class RecommendationRequest(BaseModel):
    title: str
    contents: str

class RecommendationResponse(BaseModel):
    message: str
    confirm: str

# 하드웨어 응답 시뮬레이션 데이터
HARDWARE_RESPONSES = {
    "에어컨 킬까요?": {"confirm": "YES"},
    "에어컨 끌까요?": {"confirm": "NO"},
    "공기청정기 켤까요?": {"confirm": "YES"},
    "공기청정기 끌까요?": {"confirm": "NO"},
    "건조기 켤까요?": {"confirm": "YES"},
    "건조기 끌까요?": {"confirm": "NO"},
    "온도 낮출까요?": {"confirm": "NO"}
}

@hardware_app.post("/api/recommendations", response_model=RecommendationResponse)
async def receive_recommendation(request: RecommendationRequest):
    """AI에서 받은 추천에 대한 실제 사용자 응답"""
    logger.info(f"📱 하드웨어가 추천 수신:")
    logger.info(f"  - 제목: \"{request.title}\"")
    logger.info(f"  - 내용: \"{request.contents}\"")
    
    # 실제 사용자 입력 받기
    print(f"\n🤖 AI 추천: {request.title}")
    print(f"📄 내용: {request.contents}")
    print(f"\n❓ 이 추천을 실행하시겠습니까?")
    
    while True:
        try:
            user_input = input("YES/NO 입력: ").strip().upper()
            if user_input in ["YES", "NO"]:
                break
            else:
                print("❌ YES 또는 NO만 입력하세요.")
        except KeyboardInterrupt:
            user_input = "NO"
            break
    
    logger.info(f"👤 사용자 응답: {user_input}")
    
    return RecommendationResponse(
        message=f"사용자 응답: {user_input}",
        confirm=user_input
    )

@hardware_app.get("/health")
async def hardware_health():
    return {"status": "healthy", "service": "Mock Hardware"}

# Mock Gateway 서버
gateway_app = FastAPI(title="Mock Gateway Server", version="1.0.0")

class ControlRequest(BaseModel):
    device_id: str
    action: str

class ControlResponse(BaseModel):
    message: str

@gateway_app.post("/api/lg/control", response_model=ControlResponse)
async def control_device(request: ControlRequest):
    """LG 기기 제어 시뮬레이션"""
    logger.info(f"🔧 Gateway가 기기 제어 요청 수신:")
    logger.info(f"  - 기기: {request.device_id}")
    logger.info(f"  - 액션: {request.action}")
    
    # 실제 제어 시뮬레이션
    print(f"\n🔧 Gateway 기기 제어 실행:")
    print(f"  📱 기기 ID: {request.device_id}")
    print(f"  ⚡ 액션: {request.action}")
    print(f"  🔄 제어 중...")
    
    # 시뮬레이션된 제어 실행 (더 현실적인 지연)
    await asyncio.sleep(1.0)  # 제어 지연 시뮬레이션
    
    # 기기별 응답 메시지 생성
    device_type = "알 수 없는 기기"
    if "air_purifier" in request.device_id or "공기청정기" in request.device_id:
        device_type = "공기청정기"
    elif "dryer" in request.device_id or "건조기" in request.device_id:
        device_type = "건조기"
    elif "ac" in request.device_id or "에어컨" in request.device_id:
        device_type = "에어컨"
    elif "washer" in request.device_id or "트롬" in request.device_id:
        device_type = "트롬 세탁기"
    
    action_text = "켜기" if request.action == "turn_on" else "끄기" if request.action == "turn_off" else request.action
    
    print(f"  ✅ {device_type} {action_text} 완료!")
    logger.info(f"✅ 기기 제어 완료: {device_type} -> {action_text}")
    
    message = f"[GATEWAY] {device_type} {action_text} 제어 완료"
    
    return ControlResponse(message=message)

@gateway_app.get("/api/lg/devices")
async def get_devices():
    """Gateway에서 사용 가능한 기기 목록 조회 (Mock 데이터)"""
    import hashlib
    import time
    
    # 동적으로 Mock 기기 ID 생성 (보안 강화)
    base_time = int(time.time())
    mock_devices = [
        {
            "deviceId": hashlib.sha256(f"mock_ac_{base_time}".encode()).hexdigest(),
            "deviceInfo": {
                "deviceType": "DEVICE_AIR_CONDITIONER",
                "modelName": "MOCK_AC_MODEL",
                "alias": "Mock 에어컨",
                "reportable": True
            }
        },
        {
            "deviceId": hashlib.sha256(f"mock_washer_{base_time}".encode()).hexdigest(),
            "deviceInfo": {
                "deviceType": "DEVICE_WASHER",
                "modelName": "MOCK_WASHER_MODEL",
                "alias": "Mock 세탁기",
                "reportable": True
            }
        },
        {
            "deviceId": hashlib.sha256(f"mock_purifier_{base_time}".encode()).hexdigest(),
            "deviceInfo": {
                "deviceType": "DEVICE_AIR_PURIFIER",
                "modelName": "MOCK_PURIFIER_MODEL",
                "alias": "Mock 공기청정기",
                "reportable": True
            }
        },
        {
            "deviceId": hashlib.sha256(f"mock_dryer_{base_time}".encode()).hexdigest(),
            "deviceInfo": {
                "deviceType": "DEVICE_DRYER",
                "modelName": "MOCK_DRYER_MODEL",
                "alias": "Mock 건조기",
                "reportable": True
            }
        }
    ]
    
    return {
        "messageId": "mock_gateway_response",
        "timestamp": "2025-10-24T02:05:38.733113",
        "response": mock_devices
    }

@gateway_app.get("/api/lg/devices/{device_id}/profile")
async def get_device_profile(device_id: str):
    """특정 기기의 프로필 정보 조회"""
    return {
        "messageId": "eW9neXVpX3RoaW5nX2FwaV",
        "timestamp": "2025-10-24T02:06:14.401382",
        "response": {
            "property": {
                "runState": {
                    "currentState": {
                        "type": "enum",
                        "mode": ["r"],
                        "value": {"r": ["DETECTING", "RUNNING", "ERROR", "INITIAL", "POWER_OFF", "COOLING", "WRINKLE_CARE", "RESERVED", "END", "PAUSE"]}
                    }
                },
                "operation": {
                    "dryerOperationMode": {
                        "type": "enum",
                        "mode": ["w"],
                        "value": {"w": ["START", "STOP", "POWER_OFF", "POWER_ON"]}
                    }
                },
                "remoteControlEnable": {
                    "remoteControlEnabled": {
                        "type": "boolean",
                        "mode": ["r"],
                        "value": {"r": [False, True]}
                    }
                }
            }
        }
    }

@gateway_app.get("/health")
async def gateway_health():
    return {"status": "healthy", "service": "Mock Gateway"}

async def start_servers():
    """모든 Mock 서버 시작"""
    print("🚀 Mock 서버들 시작 중...")
    
    # 하드웨어 서버 (포트 8080)
    hardware_config = uvicorn.Config(
        hardware_app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
    hardware_server = uvicorn.Server(hardware_config)
    
    # Gateway 서버 (포트 9000)
    gateway_config = uvicorn.Config(
        gateway_app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
    gateway_server = uvicorn.Server(gateway_config)
    
    print("✅ Mock 서버들 시작 완료!")
    print("  - 하드웨어 서버: http://localhost:8080")
    print("  - Gateway 서버: http://localhost:9000")
    print("\n📋 사용 가능한 엔드포인트:")
    print("  하드웨어:")
    print("    POST /api/recommendations - AI 추천 수신")
    print("    GET  /health - 상태 확인")
    print("  Gateway:")
    print("    POST /api/lg/control - LG 기기 제어")
    print("    GET  /health - 상태 확인")
    print("\n🔄 서버들을 종료하려면 Ctrl+C를 누르세요.")
    
    # 두 서버를 병렬로 실행
    await asyncio.gather(
        hardware_server.serve(),
        gateway_server.serve()
    )

if __name__ == "__main__":
    asyncio.run(start_servers())

