"""
GazeHome AI Services - LG Control Models
LG 기기 제어 관련 데이터 모델
"""

from pydantic import BaseModel, Field


class LGControlRequest(BaseModel):
    """LG 스마트기기 제어 요청 (명세서)"""
    device_id: str = Field(..., description="기기 ID (예: b403...)")
    action: str = Field(..., description="제어 액션 (turn_on/turn_off/clean/auto 중 하나)")


class LGControlResponse(BaseModel):
    """LG 스마트기기 제어 응답 (명세서)"""
    message: str
