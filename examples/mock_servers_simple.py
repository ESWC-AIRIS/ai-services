"""
GazeHome AI Services - 간단한 Mock 서버들
API 명세서 데모를 위한 Mock Gateway 및 Hardware 서버

실행 방법:
    PYTHONPATH=. python examples/mock_servers_simple.py
"""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

# Mock Gateway 서버
gateway_app = FastAPI(title="Mock Gateway Server", version="1.0.0")

class GatewayControlRequest(BaseModel):
    device_id: str
    action: str

class GatewayControlResponse(BaseModel):
    message: str

@gateway_app.post("/api/lg/control", response_model=GatewayControlResponse)
async def gateway_control_device(request: GatewayControlRequest):
    """Gateway 기기 제어 시뮬레이션"""
    logger.info(f"🔧 Gateway가 기기 제어 요청 수신:")
    logger.info(f"  - 기기: {request.device_id}")
    logger.info(f"  - 액션: {request.action}")
    
    # 시뮬레이션된 제어 실행
    await asyncio.sleep(0.5)  # 제어 지연 시뮬레이션
    
    logger.info(f"✅ Gateway 기기 제어 완료: {request.device_id} -> {request.action}")
    
    return GatewayControlResponse(
        message="[GATEWAY] 스마트 기기 제어 완료"
    )

@gateway_app.get("/health")
async def gateway_health():
    return {"status": "healthy", "service": "Mock Gateway"}

# Mock Hardware 서버
hardware_app = FastAPI(title="Mock Hardware Server", version="1.0.0")

class HardwareRecommendationRequest(BaseModel):
    title: str
    contents: str

class HardwareRecommendationResponse(BaseModel):
    message: str
    confirm: str

# 하드웨어 응답 시뮬레이션 데이터
HARDWARE_RESPONSES = {
    "에어컨 킬까요?": "YES",
    "조명 끌까요?": "NO", 
    "TV 켤까요?": "YES",
    "공기청정기 켤까요?": "YES",
    "온도 낮출까요?": "NO"
}

@hardware_app.post("/api/recommendations/", response_model=HardwareRecommendationResponse)
async def hardware_receive_recommendation(request: HardwareRecommendationRequest):
    """하드웨어가 AI 추천을 수신하고 사용자 응답 시뮬레이션"""
    logger.info(f"📱 하드웨어가 추천 수신:")
    logger.info(f"  - 제목: \"{request.title}\"")
    logger.info(f"  - 내용: \"{request.contents}\"")
    
    # 시뮬레이션된 사용자 응답
    confirm = HARDWARE_RESPONSES.get(request.title, "NO")
    
    logger.info(f"👤 사용자 응답: {confirm}")
    
    return HardwareRecommendationResponse(
        message="추천 문구 유저 피드백",
        confirm=confirm
    )

@hardware_app.get("/health")
async def hardware_health():
    return {"status": "healthy", "service": "Mock Hardware"}

async def start_servers():
    """모든 Mock 서버 시작"""
    print("🚀 Mock 서버들 시작 중...")
    
    # 환경변수에서 설정 가져오기 (하드코딩 제거)
    gateway_port = int(os.getenv("GATEWAY_PORT", "9000"))
    hardware_port = int(os.getenv("HARDWARE_PORT", "8080"))
    gateway_host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    hardware_host = os.getenv("HARDWARE_HOST", "0.0.0.0")
    
    # Gateway 서버
    gateway_config = uvicorn.Config(
        gateway_app,
        host=gateway_host,
        port=gateway_port,
        log_level="info"
    )
    gateway_server = uvicorn.Server(gateway_config)
    
    # Hardware 서버
    hardware_config = uvicorn.Config(
        hardware_app,
        host=hardware_host,
        port=hardware_port,
        log_level="info"
    )
    hardware_server = uvicorn.Server(hardware_config)
    
    print("✅ Mock 서버들 시작 완료!")
    print(f"  - Gateway 서버: http://{gateway_host}:{gateway_port}")
    print(f"  - Hardware 서버: http://{hardware_host}:{hardware_port}")
    print("\n📋 사용 가능한 엔드포인트:")
    print("  Gateway:")
    print("    POST /api/lg/control - LG 기기 제어")
    print("    GET  /health - 상태 확인")
    print("  Hardware:")
    print("    POST /api/recommendations - AI 추천 수신")
    print("    GET  /health - 상태 확인")
    print("\n🔄 서버들을 종료하려면 Ctrl+C를 누르세요.")
    
    # 두 서버를 병렬로 실행
    await asyncio.gather(
        gateway_server.serve(),
        hardware_server.serve()
    )

if __name__ == "__main__":
    asyncio.run(start_servers())
