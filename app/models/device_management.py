"""
GazeHome AI Services - Device Management Models
MongoDB 기기 관리 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum


from app.models.user import PyObjectId


class DeviceType(str, Enum):
    """기기 타입"""
    AIR_PURIFIER = "air_purifier"
    DRYER = "dryer"
    AIR_CONDITIONER = "air_conditioner"


class DeviceAction(BaseModel):
    """기기 액션"""
    action: str = Field(..., description="액션명")
    description: str = Field(..., description="액션 설명")
    parameters: Optional[Dict[str, Any]] = Field(None, description="액션 파라미터")


class UserDevice(BaseModel):
    """사용자 기기 정보"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str = Field(..., description="사용자 ID")
    device_id: str = Field(..., description="Gateway 기기 ID")
    device_type: DeviceType = Field(..., description="기기 타입")
    alias: str = Field(..., description="사용자 지정 별명")
    supported_actions: List[str] = Field(..., description="지원하는 액션 목록")
    is_active: bool = Field(default=True, description="활성 상태")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceRegistrationRequest(BaseModel):
    """기기 등록 요청"""
    device_id: str = Field(..., description="Gateway 기기 ID")
    device_type: DeviceType = Field(..., description="기기 타입")
    alias: str = Field(..., description="사용자 지정 별명")
    supported_actions: List[str] = Field(..., description="지원하는 액션 목록")


class DeviceRegistrationResponse(BaseModel):
    """기기 등록 응답"""
    message: str
    device_id: str


class DeviceListResponse(BaseModel):
    """기기 목록 응답"""
    devices: List[UserDevice]


# 기기 타입별 지원 액션 매핑
DEVICE_ACTIONS = {
    DeviceType.AIR_PURIFIER: ["turn_on", "turn_off", "clean", "auto"],
    DeviceType.DRYER: ["dryer_on", "dryer_off", "dryer_start", "dryer_stop"],
    DeviceType.AIR_CONDITIONER: ["aircon_on", "aircon_off"] + [f"temp_{i}" for i in range(18, 31)]
}


def get_supported_actions(device_type: DeviceType) -> List[str]:
    """기기 타입별 지원 액션 반환"""
    return DEVICE_ACTIONS.get(device_type, [])
