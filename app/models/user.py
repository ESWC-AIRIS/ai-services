"""
GazeHome AI Services - User Models
사용자 관련 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


# PyObjectId를 단순한 문자열 타입으로 사용
PyObjectId = str


class User(BaseModel):
    """사용자 모델"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str = Field(..., description="사용자 고유 ID")
    name: str = Field(..., description="사용자 이름")
    email: Optional[str] = Field(None, description="이메일")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="사용자 선호도")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInteraction(BaseModel):
    """사용자 상호작용 모델"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str = Field(..., description="사용자 ID")
    interaction_type: str = Field(..., description="상호작용 유형 (gaze, voice, touch)")
    data: Dict[str, Any] = Field(..., description="상호작용 데이터")
    context: Dict[str, Any] = Field(default_factory=dict, description="맥락 정보")
    result: Optional[Dict[str, Any]] = Field(None, description="결과")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
