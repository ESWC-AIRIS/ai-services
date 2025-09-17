"""
GazeHome AI Services - API Router
API 엔드포인트 라우터 설정
"""

from fastapi import APIRouter
from app.api.endpoints import gaze, context, automation, devices

# API 라우터 생성
api_router = APIRouter()

# 엔드포인트 라우터 등록
api_router.include_router(
    gaze.router,
    prefix="/gaze",
    tags=["gaze-control"]
)

api_router.include_router(
    context.router,
    prefix="/context",
    tags=["context-analysis"]
)

api_router.include_router(
    automation.router,
    prefix="/automation",
    tags=["automation"]
)

api_router.include_router(
    devices.router,
    prefix="/devices",
    tags=["device-control"]
)
