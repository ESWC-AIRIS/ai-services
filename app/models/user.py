"""
GazeHome AI Services - User Models
사용자 관련 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """MongoDB ObjectId를 Pydantic과 호환되도록 하는 클래스"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    """사용자 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="사용자 고유 ID")
    name: str = Field(..., description="사용자 이름")
    email: Optional[str] = Field(None, description="이메일")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="사용자 선호도")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInteraction(BaseModel):
    """사용자 상호작용 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="사용자 ID")
    interaction_type: str = Field(..., description="상호작용 유형 (gaze, voice, touch)")
    data: Dict[str, Any] = Field(..., description="상호작용 데이터")
    context: Dict[str, Any] = Field(default_factory=dict, description="맥락 정보")
    result: Optional[Dict[str, Any]] = Field(None, description="결과")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
