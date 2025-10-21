"""
GazeHome AI Services - Scheduler Endpoints
능동적 추천 스케줄러 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import pytz

from app.core.scheduler import get_scheduler
from app.core.config import settings

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')


class SchedulerStatus(BaseModel):
    """스케줄러 상태 모델"""
    is_running: bool
    is_enabled: bool
    interval_minutes: int
    jobs: list
    timezone: str
    timestamp: str


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status():
    """
    스케줄러 상태 조회
    
    Returns:
        스케줄러 실행 상태 및 작업 정보
    """
    try:
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        return SchedulerStatus(
            is_running=status['is_running'],
            is_enabled=settings.PROACTIVE_RECOMMENDATION_ENABLED,
            interval_minutes=settings.PROACTIVE_RECOMMENDATION_INTERVAL_MINUTES,
            jobs=status['jobs'],
            timezone=status['timezone'],
            timestamp=datetime.now(KST).isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"스케줄러 상태 조회 실패: {str(e)}"
        )


@router.post("/trigger")
async def trigger_recommendations():
    """
    능동적 추천 즉시 실행 (테스트용)
    
    주기를 기다리지 않고 즉시 추천 작업을 실행합니다.
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            raise HTTPException(
                status_code=400,
                detail="스케줄러가 실행 중이 아닙니다"
            )
        
        # 추천 작업 즉시 실행
        await scheduler._run_proactive_recommendations()
        
        return {
            "status": "success",
            "message": "능동적 추천 작업 실행 완료",
            "timestamp": datetime.now(KST).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"추천 작업 실행 실패: {str(e)}"
        )

