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
    message: str

class RecommendationResponse(BaseModel):
    message: str
    confirm: str

# 하드웨어 응답 시뮬레이션 데이터
HARDWARE_RESPONSES = {
    "에어컨 킬까요?": {"confirm": "YES"},
    "조명 끌까요?": {"confirm": "NO"},
    "TV 켤까요?": {"confirm": "YES"},
    "공기청정기 켤까요?": {"confirm": "YES"},
    "온도 낮출까요?": {"confirm": "NO"}
}

@hardware_app.post("/api/recommendations", response_model=RecommendationResponse)
async def receive_recommendation(request: RecommendationRequest):
    """AI에서 받은 추천에 대한 사용자 응답 시뮬레이션"""
    logger.info(f"📱 하드웨어가 추천 수신: \"{request.message}\"")
    
    # 시뮬레이션된 사용자 응답
    response = HARDWARE_RESPONSES.get(request.message, {"confirm": "NO"})
    
    logger.info(f"👤 사용자 응답: {response['confirm']}")
    
    return RecommendationResponse(
        message="추천 문구 유저 피드백",
        confirm=response["confirm"]
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
    
    # 시뮬레이션된 제어 실행
    await asyncio.sleep(0.5)  # 제어 지연 시뮬레이션
    
    logger.info(f"✅ 기기 제어 완료: {request.device_id} -> {request.action}")
    
    return ControlResponse(
        message="[GATEWAY] 스마트 기기 제어 완료"
    )

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

