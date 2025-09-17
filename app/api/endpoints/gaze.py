"""
GazeHome AI Services - Gaze Control Endpoints
시선 제어 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pytz

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')


class GazeData(BaseModel):
    """시선 데이터 모델"""
    x: float
    y: float
    timestamp: datetime
    confidence: float
    user_id: str


class GazeCommand(BaseModel):
    """시선 명령 모델"""
    gaze_data: GazeData
    context: Optional[dict] = None


@router.post("/track")
async def track_gaze(gaze_data: GazeData):
    """시선 추적 데이터 수신"""
    try:
        # 시선 데이터 처리 로직 (추후 구현)
        return {
            "status": "success",
            "message": "시선 데이터 수신 완료",
            "timestamp": datetime.now(KST).isoformat(),
            "data": gaze_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/command")
async def process_gaze_command(command: GazeCommand):
    """시선 기반 명령 처리"""
    try:
        # 시선 명령 처리 로직 (추후 구현)
        return {
            "status": "success",
            "message": "시선 명령 처리 완료",
            "timestamp": datetime.now(KST).isoformat(),
            "command": command
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_gaze_status():
    """시선 추적 상태 확인"""
    return {
        "status": "active",
        "timestamp": datetime.now(KST).isoformat(),
        "message": "시선 추적 시스템 정상 작동 중"
    }
