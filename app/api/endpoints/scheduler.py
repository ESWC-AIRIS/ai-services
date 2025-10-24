"""
스케줄러 제어 API 엔드포인트
스마트 홈 추천 스케줄러를 시작/중지하고 상태를 확인할 수 있는 API
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from app.services.scheduler_service import scheduler_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

class SchedulerStartRequest(BaseModel):
    """스케줄러 시작 요청"""
    user_id: str = Field(default="default_user", description="사용자 ID")
    interval_minutes: int = Field(default=30, ge=1, le=1440, description="실행 간격 (분)")

class SchedulerStatusResponse(BaseModel):
    """스케줄러 상태 응답"""
    is_running: bool
    user_id: str
    interval_minutes: int
    last_check: str

class RecommendationTestResponse(BaseModel):
    """추천 테스트 응답"""
    should_recommend: bool
    title: Optional[str] = None
    contents: Optional[str] = None
    reason: Optional[str] = None
    timestamp: str

@router.post("/start", response_model=Dict[str, str])
async def start_scheduler(request: SchedulerStartRequest):
    """스케줄러 시작"""
    try:
        await scheduler_service.start(
            user_id=request.user_id,
            interval_minutes=request.interval_minutes
        )
        return {
            "message": f"스케줄러가 시작되었습니다 (사용자: {request.user_id}, 간격: {request.interval_minutes}분)"
        }
    except Exception as e:
        logger.error(f"스케줄러 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스케줄러 시작 실패: {e}")

@router.post("/stop", response_model=Dict[str, str])
async def stop_scheduler():
    """스케줄러 중지"""
    try:
        await scheduler_service.stop()
        return {"message": "스케줄러가 중지되었습니다"}
    except Exception as e:
        logger.error(f"스케줄러 중지 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스케줄러 중지 실패: {e}")

@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """스케줄러 상태 확인"""
    try:
        status = scheduler_service.get_status()
        return SchedulerStatusResponse(**status)
    except Exception as e:
        logger.error(f"스케줄러 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {e}")

@router.post("/test", response_model=RecommendationTestResponse)
async def test_recommendation(user_id: str = "default_user"):
    """추천 테스트 (한 번만 실행)"""
    try:
        result = await scheduler_service.run_once(user_id)
        return RecommendationTestResponse(**result)
    except Exception as e:
        logger.error(f"추천 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 테스트 실패: {e}")

@router.post("/restart", response_model=Dict[str, str])
async def restart_scheduler(request: SchedulerStartRequest):
    """스케줄러 재시작"""
    try:
        # 먼저 중지
        await scheduler_service.stop()
        
        # 잠시 대기
        import asyncio
        await asyncio.sleep(1)
        
        # 다시 시작
        await scheduler_service.start(
            user_id=request.user_id,
            interval_minutes=request.interval_minutes
        )
        
        return {
            "message": f"스케줄러가 재시작되었습니다 (사용자: {request.user_id}, 간격: {request.interval_minutes}분)"
        }
    except Exception as e:
        logger.error(f"스케줄러 재시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스케줄러 재시작 실패: {e}")

