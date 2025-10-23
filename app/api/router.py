"""
GazeHome AI Services - API Router
API 엔드포인트 라우터 설정 (명세서에 맞춤)
"""

from fastapi import APIRouter
from app.api.endpoints import devices, recommendations

# API 라우터 생성
api_router = APIRouter()

# 명세서에 맞는 엔드포인트들만 등록
api_router.include_router(
    devices.router,
    prefix="/lg",
    tags=["lg-control"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["smart-recommendations"]
)