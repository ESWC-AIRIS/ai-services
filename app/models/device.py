"""
GazeHome AI Services - Device Models
기기 관련 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId


class Device(BaseModel):
    """기기 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str = Field(..., description="기기 고유 ID")
    name: str = Field(..., description="기기 이름")
    type: str = Field(..., description="기기 유형 (light, tv, air_conditioner, etc.)")
    brand: str = Field(..., description="브랜드")
    model: Optional[str] = Field(None, description="모델명")
    location: Optional[str] = Field(None, description="설치 위치")
    status: str = Field(default="off", description="현재 상태")
    capabilities: List[str] = Field(default_factory=list, description="지원 기능")
    settings: Dict[str, Any] = Field(default_factory=dict, description="기기 설정")
    user_id: str = Field(..., description="소유자 사용자 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceCommand(BaseModel):
    """기기 명령 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str = Field(..., description="대상 기기 ID")
    user_id: str = Field(..., description="명령 사용자 ID")
    action: str = Field(..., description="실행할 액션")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="액션 파라미터")
    status: str = Field(default="pending", description="명령 상태 (pending, executing, completed, failed)")
    result: Optional[Dict[str, Any]] = Field(None, description="실행 결과")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DeviceState(BaseModel):
    """기기 상태 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str = Field(..., description="기기 ID")
    state: Dict[str, Any] = Field(..., description="기기 상태 정보")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
