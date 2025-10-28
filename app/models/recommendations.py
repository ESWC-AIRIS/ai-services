"""
GazeHome AI Services - Recommendation Models
MongoDB 추천 관리 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

from app.models.user import PyObjectId


class RecommendationStatus(str, Enum):
    """추천 상태"""
    PENDING = "pending"           # 대기중 (하드웨어에 전송됨)
    CONFIRMED = "confirmed"       # 승인됨 (사용자가 YES)
    REJECTED = "rejected"        # 거부됨 (사용자가 NO)
    EXPIRED = "expired"          # 만료됨 (시간 초과)


class DeviceControl(BaseModel):
    """기기 제어 정보"""
    device_type: str = Field(..., description="기기 타입 (air_purifier, dryer, air_conditioner)")
    action: str = Field(..., description="제어 액션")
    device_id: Optional[str] = Field(None, description="기기 ID")


class Recommendation(BaseModel):
    """추천 정보"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    recommendation_id: str = Field(..., description="추천 ID (rec_YYYYMMDD_HHMMSS)")
    user_id: str = Field(..., description="추천을 받은 사용자 ID")
    title: str = Field(..., description="추천 제목")
    contents: str = Field(..., description="추천 내용")
    context: Optional[str] = Field(None, description="추천 컨텍스트")
    device_control: Optional[DeviceControl] = Field(None, description="기기 제어 정보")
    status: RecommendationStatus = Field(default=RecommendationStatus.PENDING, description="추천 상태")
    mode: str = Field(..., description="데모/운영 구분 (demo/production)")
    user_response: Optional[str] = Field(None, description="사용자 응답 (YES/NO)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    confirmed_at: Optional[datetime] = Field(None, description="확인 시간")
    hardware_sent_at: Optional[datetime] = Field(None, description="하드웨어 전송 시간")
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RecommendationCreateRequest(BaseModel):
    """데모용 추천 생성 요청"""
    user_id: str = Field(..., description="추천을 요청한 사용자 ID")
    scenario: str = Field(..., description="데모 시나리오명 (예: '여름폭염', '겨울한파')")


class HardwareRecommendationRequest(BaseModel):
    """하드웨어용 추천 전달 요청 (명세서)"""
    recommendation_id: str = Field(..., description="추천 ID")
    title: str = Field(..., description="추천 제목")
    contents: str = Field(..., description="추천 내용")
    user_id: Optional[str] = Field("default_user", description="사용자 ID")
    device_control: Optional[DeviceControl] = Field(None, description="기기 제어 정보")


class RecommendationCreateResponse(BaseModel):
    """추천 생성 응답"""
    recommendation_id: str = Field(..., description="추천 ID")
    message: str = Field(..., description="응답 메시지")


class RecommendationConfirmRequest(BaseModel):
    """추천 확인 요청"""
    recommendation_id: str = Field(..., description="추천 ID")
    confirm: str = Field(..., description="사용자 응답 (YES/NO)")


class RecommendationConfirmResponse(BaseModel):
    """추천 확인 응답"""
    recommendation_id: str = Field(..., description="추천 ID")
    message: str = Field(..., description="응답 메시지")


class RecommendationResponse(BaseModel):
    """추천 조회 응답"""
    recommendation_id: str = Field(..., description="추천 ID")
    title: str = Field(..., description="추천 제목")
    contents: str = Field(..., description="추천 내용")
    context: Optional[str] = Field(None, description="추천 컨텍스트")
    device_control: Optional[DeviceControl] = Field(None, description="기기 제어 정보")
    status: RecommendationStatus = Field(..., description="추천 상태")
    user_response: Optional[str] = Field(None, description="사용자 응답")
    created_at: datetime = Field(..., description="생성 시간")
    confirmed_at: Optional[datetime] = Field(None, description="확인 시간")


def generate_recommendation_id() -> str:
    """추천 ID 생성 (rec_YYYYMMDD_HHMMSS)"""
    now = datetime.utcnow()
    return f"rec_{now.strftime('%Y%m%d_%H%M%S')}"