"""
GazeHome AI Services - Recommendation Models
AI 추천 시스템 관련 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class RecommendationRequest(BaseModel):
    """AI → HW 추천 요청 (명세서)"""
    title: str = Field(..., description="추천 제목 (예: 에어컨 킬까요?)")
    contents: str = Field(..., description="추천 내용")


class DeviceControlInfo(BaseModel):
    """기기 제어 정보"""
    device_id: str = Field(..., description="기기 ID")
    device_type: str = Field(..., description="기기 타입")
    action: str = Field(..., description="제어 액션")
    device_alias: str = Field(..., description="기기 별명")


class RecommendationResponse(BaseModel):
    """AI → HW 추천 응답 (명세서)"""
    message: str
    confirm: str = Field(..., description="사용자 확인 (YES/NO)")
    device_control: Optional[DeviceControlInfo] = Field(None, description="기기 제어 정보")


class EnhancedRecommendation(BaseModel):
    """향상된 추천 정보 (제어 정보 포함)"""
    title: str = Field(..., description="추천 제목")
    contents: str = Field(..., description="추천 내용")
    device_control: Optional[DeviceControlInfo] = Field(None, description="기기 제어 정보")
