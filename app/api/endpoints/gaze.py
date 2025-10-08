"""
GazeHome AI Services - Gaze Control Endpoints
시선 제어 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import pytz
from app.services.llm_service import LLMService
from app.services.mongodb_service import MongoDBService

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')

# 서비스 인스턴스
llm_service = LLMService()
db_service = MongoDBService()


class DeviceClickInfo(BaseModel):
    """클릭된 기기 정보"""
    device_id: str  # "device_001"
    device_type: str  # "air_conditioner", "light", "tv", etc.
    device_name: str  # "거실 에어컨"
    display_name: str  # "에어컨"
    capabilities: List[str] = []  # ["on_off", "temperature", "mode"]
    current_state: Dict[str, Any] = {}  # {"is_on": false, "temperature": 24}


class GazeClickRequest(BaseModel):
    """하드웨어에서 받는 시선 클릭 요청"""
    user_id: str
    session_id: str
    clicked_device: DeviceClickInfo  # 클릭된 IoT 기기 정보
    timestamp: datetime = Field(default_factory=lambda: datetime.now(KST))
    context: Optional[Dict[str, Any]] = {}  # 추가 컨텍스트 정보


class GazeClickResponse(BaseModel):
    """시선 클릭 처리 응답"""
    status: str
    message: str
    session_id: str
    clicked_device_id: str
    recommendation: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(KST))


@router.post("/click", response_model=GazeClickResponse)
async def process_device_click(request: GazeClickRequest):
    """
    하드웨어에서 전송한 IoT 기기 클릭 이벤트 처리
    
    하드웨어가 시선 추적으로 사용자가 특정 IoT 기기를 클릭했다는 정보를 전송하면,
    LLM Agent를 통해 심층적 의도를 추론하고 최적의 다음 명령어를 추천합니다.
    """
    try:
        clicked_device = request.clicked_device
        
        # ============================================================
        # MongoDB 저장 로직 (선택사항)
        # ============================================================
        # 현재는 비활성화되어 있습니다. 필요시 아래 주석을 해제하세요.
        # 
        # 저장이 필요한 경우:
        # - 사용자별 패턴 학습
        # - AI 추천 정확도 개선
        # - 서비스 품질 모니터링
        # - 사용자 행동 분석
        # 
        # 활성화 방법:
        # 1. 아래 주석 제거
        # 2. MongoDB 연결 확인
        # 3. 컬렉션 인덱스 설정
        # ============================================================
        
        # click_event = {
        #     "user_id": request.user_id,
        #     "session_id": request.session_id,
        #     "clicked_device_id": clicked_device.device_id,
        #     "clicked_device_type": clicked_device.device_type,
        #     "clicked_device_name": clicked_device.device_name,
        #     "current_state": clicked_device.current_state,
        #     "timestamp": request.timestamp,
        #     "context": request.context
        # }
        # await db_service.insert_one("device_click_events", click_event)
        
        # LLM을 통한 의도 추론 및 추천 생성
        intent_context = {
            "clicked_device": clicked_device.dict(),
            "user_id": request.user_id,
            "session_id": request.session_id,
            "context": request.context
        }
        
        # LLM 서비스를 통해 추천 생성
        recommendation = await llm_service.generate_device_recommendation(
            device_info=clicked_device.dict(),
            context=intent_context
        )
        
        # ============================================================
        # 추천 결과 저장 (선택사항)
        # ============================================================
        # recommendation_record = {
        #     "session_id": request.session_id,
        #     "user_id": request.user_id,
        #     "clicked_device_id": clicked_device.device_id,
        #     "recommendation": recommendation,
        #     "timestamp": datetime.now(KST)
        # }
        # await db_service.insert_one("device_click_recommendations", recommendation_record)
        # ============================================================
        
        return GazeClickResponse(
            status="success",
            message=f"{clicked_device.display_name} 클릭 처리 완료",
            session_id=request.session_id,
            clicked_device_id=clicked_device.device_id,
            recommendation=recommendation,
            timestamp=datetime.now(KST)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"기기 클릭 처리 실패: {str(e)}"
        )


@router.get("/status")
async def get_gaze_status():
    """시선 추적 시스템 상태 확인"""
    return {
        "status": "active",
        "timestamp": datetime.now(KST).isoformat(),
        "message": "시선 클릭 기반 IoT 제어 시스템 정상 작동 중",
        "mode": "device_click"
    }
