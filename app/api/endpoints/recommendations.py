"""
GazeHome AI Services - Recommendation Response Endpoints
하드웨어로부터 사용자 응답을 받는 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import pytz

from app.services.device_control_service import get_device_control_service
from app.services.llm_service import LLMService
from app.services.mongodb_service import MongoDBService

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')

# 서비스 인스턴스
device_control_service = get_device_control_service()
llm_service = LLMService()
db_service = MongoDBService()


class RecommendationResponse(BaseModel):
    """하드웨어로부터 받는 사용자 응답"""
    user_id: str
    recommendation_id: Optional[str] = None  # 추천 ID (있으면)
    accepted: bool  # True: 네(수락), False: 아니요(거부)
    device_id: str  # 추천된 기기 ID
    action: Dict[str, Any]  # 추천된 액션
    timestamp: datetime = Field(default_factory=lambda: datetime.now(KST))


class RecommendationResponseResult(BaseModel):
    """응답 처리 결과"""
    status: str
    message: str
    executed: bool  # 기기 제어 실행 여부
    timestamp: datetime = Field(default_factory=lambda: datetime.now(KST))


@router.post("/response", response_model=RecommendationResponseResult)
async def handle_recommendation_response(response: RecommendationResponse):
    """
    하드웨어로부터 사용자 응답 수신 및 처리
    
    사용자가 추천을 수락(Y)하면 → 기기 제어 실행
    사용자가 추천을 거부(N)하면 → 피드백 학습
    """
    try:
        logger_prefix = f"[{response.user_id}]"
        
        if response.accepted:
            # ✅ 수락: 기기 제어 실행
            logger.info(f"{logger_prefix} ✅ 사용자가 추천 수락")
            logger.info(f"{logger_prefix} 기기 제어 실행 중...")
            
            # 기기 제어 실행
            executed = await device_control_service.execute_device_command(
                device_id=response.device_id,
                command=response.action.get('command'),
                parameters=response.action.get('parameters', {})
            )
            
            if executed:
                logger.info(f"{logger_prefix} ✅ 기기 제어 성공!")
                
                # Long-term Memory에 긍정적 피드백 학습
                try:
                    await llm_service.memory.long_term.learn_from_interaction(
                        user_id=response.user_id,
                        interaction={
                            'device_id': response.device_id,
                            'action': response.action.get('command'),
                            'accepted': True,
                            'timestamp': response.timestamp
                        }
                    )
                    logger.info(f"{logger_prefix} 긍정적 피드백 학습 완료")
                except Exception as e:
                    logger.warning(f"{logger_prefix} 피드백 학습 실패: {e}")
                
                return RecommendationResponseResult(
                    status="success",
                    message="추천이 수락되었고 기기 제어가 완료되었습니다.",
                    executed=True,
                    timestamp=datetime.now(KST)
                )
            else:
                logger.error(f"{logger_prefix} ❌ 기기 제어 실패")
                return RecommendationResponseResult(
                    status="partial_success",
                    message="추천은 수락되었으나 기기 제어에 실패했습니다.",
                    executed=False,
                    timestamp=datetime.now(KST)
                )
        
        else:
            # ❌ 거부: 피드백 학습
            logger.info(f"{logger_prefix} ❌ 사용자가 추천 거부")
            
            # Long-term Memory에 부정적 피드백 학습
            try:
                await llm_service.memory.long_term.learn_from_interaction(
                    user_id=response.user_id,
                    interaction={
                        'device_id': response.device_id,
                        'action': response.action.get('command'),
                        'accepted': False,
                        'timestamp': response.timestamp
                    }
                )
                logger.info(f"{logger_prefix} 부정적 피드백 학습 완료")
            except Exception as e:
                logger.warning(f"{logger_prefix} 피드백 학습 실패: {e}")
            
            return RecommendationResponseResult(
                status="success",
                message="추천이 거부되었습니다. 피드백이 학습되었습니다.",
                executed=False,
                timestamp=datetime.now(KST)
            )
    
    except Exception as e:
        logger.error(f"응답 처리 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"응답 처리 실패: {str(e)}"
        )


@router.get("/history/{user_id}")
async def get_recommendation_history(user_id: str):
    """
    사용자의 추천 이력 조회
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        추천 이력 목록
    """
    try:
        # TODO: MongoDB에서 추천 이력 조회
        # 현재는 예시 데이터 반환
        return {
            "status": "success",
            "user_id": user_id,
            "history": [],
            "timestamp": datetime.now(KST).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"이력 조회 실패: {str(e)}"
        )


import logging
logger = logging.getLogger(__name__)

