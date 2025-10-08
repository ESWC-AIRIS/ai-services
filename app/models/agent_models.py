"""
GazeHome AI Services - Agent Data Models
에이전트 시스템을 위한 MongoDB 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import uuid


class AgentType(str, Enum):
    """에이전트 타입"""
    INTENT_RECOGNITION = "intent_recognition"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"
    RECOMMENDATION = "recommendation"


class InteractionStatus(str, Enum):
    """상호작용 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FeedbackType(str, Enum):
    """피드백 타입"""
    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"


# 1. 시선 상호작용 데이터
class DeviceGazeData(BaseModel):
    """기기별 시선 데이터"""
    device_id: str  # "light", "air_conditioner", "tv", "air_purifier"
    gaze_probability: float  # 0.0-1.0, 해당 기기를 보고 있을 확률
    duration: float  # 응시 시간 (초)
    timestamp: datetime


class GazeInteraction(BaseModel):
    """시선 상호작용 문서"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    device_gaze_data: List[DeviceGazeData]  # 기기별 시선 확률 데이터
    total_duration: float  # 전체 응시 시간
    interaction_history: List[Dict[str, Any]] = []
    time_context: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 2. 에이전트 실행 세션
class AgentExecution(BaseModel):
    """에이전트 실행 기록"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    agent_type: AgentType
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time_ms: int
    status: InteractionStatus
    error_message: Optional[str] = None
    gemini_api_calls: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class AgentSession(BaseModel):
    """에이전트 세션 (전체 파이프라인)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    gaze_interaction_id: str
    intent_agent_execution_id: Optional[str] = None
    context_agent_execution_id: Optional[str] = None
    recommendation_agent_execution_id: Optional[str] = None
    final_recommendation: Optional[Dict[str, Any]] = None
    status: InteractionStatus = InteractionStatus.PENDING
    total_execution_time_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


# 3. 사용자 피드백
class UserFeedback(BaseModel):
    """사용자 피드백"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    recommendation_id: str
    feedback_type: FeedbackType
    user_id: str
    feedback_data: Dict[str, Any] = {}
    reasoning: Optional[str] = None
    final_action: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)


# 4. 추천 기록
class Recommendation(BaseModel):
    """추천 기록"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    prompt_text: str
    action_to_recommend: Dict[str, Any]
    contextual_insights: List[Dict[str, Any]] = []
    confidence_score: float
    personalized_recommendations: List[Dict[str, Any]] = []
    is_accepted: Optional[bool] = None
    feedback_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None


# 5. 사용자 선호도 및 패턴
class UserPreference(BaseModel):
    """사용자 선호도"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    device_id: str
    preferred_actions: List[str] = []
    time_patterns: Dict[str, Any] = {}
    environmental_preferences: Dict[str, Any] = {}
    automation_rules: List[Dict[str, Any]] = []
    last_updated: datetime = Field(default_factory=datetime.now)


# 6. 외부 환경 데이터
class EnvironmentalData(BaseModel):
    """외부 환경 데이터"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    weather_data: Dict[str, Any] = {}
    air_quality_data: Dict[str, Any] = {}
    time_context: Dict[str, Any] = {}
    location_data: Optional[Dict[str, Any]] = None


# 7. 시스템 메트릭
class SystemMetrics(BaseModel):
    """시스템 메트릭"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_type: AgentType
    execution_time_avg_ms: float
    success_rate: float
    gemini_api_calls_count: int
    error_rate: float
    user_satisfaction_score: Optional[float] = None


# API 요청/응답 모델
class GazeDataRequest(BaseModel):
    """라즈베리파이에서 받는 시선 데이터 요청 (기존 확률 기반)"""
    user_id: str
    session_id: str
    gaze_data: Dict[str, float]  # {"device_123": 0.85, "device_456": 0.12, ...}
    device_mapping: Dict[str, Dict[str, Any]]  # 기기 정보 매핑
    timestamp: datetime = Field(default_factory=datetime.now)
    device_info: Dict[str, Any] = {}  # 화면 크기, 브라우저 정보 등


class GazeDataResponse(BaseModel):
    """시선 데이터 처리 응답"""
    status: str
    message: str
    session_id: str
    detected_intent: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# 기기 클릭 이벤트 모델 (새로운 시스템)
class DeviceClickEvent(BaseModel):
    """기기 클릭 이벤트 (MongoDB 저장용)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    clicked_device_id: str
    clicked_device_type: str
    clicked_device_name: str
    current_state: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    recommendation_generated: bool = False
    recommendation_id: Optional[str] = None


class DeviceClickRecommendation(BaseModel):
    """기기 클릭 후 생성된 추천"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    click_event_id: str
    user_id: str
    session_id: str
    clicked_device_id: str
    intent: str  # 추론된 의도
    confidence: float  # 신뢰도
    prompt_text: str  # 사용자에게 보여줄 메시지
    action: Dict[str, Any]  # 추천 명령어
    reasoning: str  # 추천 이유
    is_accepted: Optional[bool] = None
    user_feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None


# 기기 관리 시스템
class DeviceType(str, Enum):
    """기기 타입"""
    LIGHT = "light"
    AIR_CONDITIONER = "air_conditioner"
    TV = "tv"
    AIR_PURIFIER = "air_purifier"
    SPEAKER = "speaker"
    CAMERA = "camera"
    DOOR_LOCK = "door_lock"
    THERMOSTAT = "thermostat"
    CUSTOM = "custom"


class DeviceCapability(str, Enum):
    """기기 기능"""
    ON_OFF = "on_off"
    BRIGHTNESS = "brightness"
    TEMPERATURE = "temperature"
    VOLUME = "volume"
    CHANNEL = "channel"
    MODE = "mode"
    COLOR = "color"
    TIMER = "timer"


class SmartDevice(BaseModel):
    """스마트 기기 정보"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    device_id: str  # UI에서 표시되는 고유 ID
    device_type: DeviceType
    name: str  # "거실 조명", "침실 에어컨" 등
    display_name: str  # UI 표시명
    capabilities: List[DeviceCapability]  # 지원하는 기능들
    current_state: Dict[str, Any] = {}  # 현재 상태
    ui_position: Dict[str, Any] = {}  # UI에서의 위치 정보
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserDeviceLayout(BaseModel):
    """사용자별 기기 레이아웃"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    layout_name: str  # "기본 레이아웃", "거실 전용" 등
    devices: List[str]  # 기기 ID 리스트 (순서대로 배치)
    screen_config: Dict[str, Any] = {}  # 화면 설정
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# MongoDB 컬렉션 매핑
COLLECTION_MAPPING = {
    "gaze_interactions": GazeInteraction,
    "agent_executions": AgentExecution,
    "agent_sessions": AgentSession,
    "user_feedback": UserFeedback,
    "recommendations": Recommendation,
    "user_preferences": UserPreference,
    "environmental_data": EnvironmentalData,
    "system_metrics": SystemMetrics,
    "smart_devices": SmartDevice,
    "user_device_layouts": UserDeviceLayout,
    "device_click_events": DeviceClickEvent,
    "device_click_recommendations": DeviceClickRecommendation,
}


# 확장 가능한 데이터 구조 예시
EXAMPLE_GAZE_REQUEST = {
    "user_id": "user_123",
    "session_id": "session_456",
    "gaze_data": {
        "device_001": 0.85,  # 조명
        "device_002": 0.12,  # 에어컨
        "device_003": 0.03,  # TV
        "device_004": 0.0    # 공기청정기
    },
    "device_mapping": {
        "device_001": {
            "device_id": "device_001",
            "device_type": "light",
            "name": "거실 조명",
            "display_name": "조명",
            "capabilities": ["on_off", "brightness", "color"],
            "ui_position": {"row": 0, "col": 0}
        },
        "device_002": {
            "device_id": "device_002", 
            "device_type": "air_conditioner",
            "name": "거실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "ui_position": {"row": 0, "col": 1}
        }
        # 새로운 기기 추가 시 여기에 추가
    },
    "device_info": {
        "screen_width": 1920,
        "screen_height": 1080,
        "device_type": "desktop",
        "browser": "chrome"
    }
}
