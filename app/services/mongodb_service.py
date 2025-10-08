"""
GazeHome AI Services - MongoDB Service
에이전트 시스템을 위한 MongoDB 데이터 관리 서비스
"""

import logging
from typing import Dict, Any, List, Optional, Type, TypeVar
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.core.database import get_database
from app.models.agent_models import (
    GazeInteraction, AgentExecution, AgentSession, UserFeedback,
    Recommendation, UserPreference, EnvironmentalData, SystemMetrics,
    DeviceGazeData, GazeDataRequest, SmartDevice, UserDeviceLayout,
    COLLECTION_MAPPING, AgentType, InteractionStatus, DeviceType
)

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)


class MongoDBService:
    """MongoDB 데이터 관리 서비스"""
    
    def __init__(self):
        self.database = get_database()
        self._collections = {}
        logger.info("MongoDB 서비스 초기화 완료")
    
    def _get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """컬렉션 인스턴스 반환"""
        if collection_name not in self._collections:
            self._collections[collection_name] = self.database[collection_name]
        return self._collections[collection_name]
    
    async def create_indexes(self):
        """컬렉션 인덱스 생성"""
        try:
            # 시선 상호작용 인덱스
            await self._get_collection("gaze_interactions").create_index([
                ("user_id", 1),
                ("created_at", -1)
            ])
            
            # 에이전트 세션 인덱스
            await self._get_collection("agent_sessions").create_index([
                ("user_id", 1),
                ("status", 1),
                ("created_at", -1)
            ])
            
            # 추천 인덱스
            await self._get_collection("recommendations").create_index([
                ("user_id", 1),
                ("created_at", -1)
            ])
            
            # 사용자 피드백 인덱스
            await self._get_collection("user_feedback").create_index([
                ("session_id", 1),
                ("created_at", -1)
            ])
            
            # 환경 데이터 인덱스
            await self._get_collection("environmental_data").create_index([
                ("timestamp", -1)
            ])
            
            logger.info("MongoDB 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {e}")
    
    # 시선 상호작용 관리
    async def save_gaze_interaction(self, interaction: GazeInteraction) -> str:
        """시선 상호작용 저장"""
        try:
            collection = self._get_collection("gaze_interactions")
            result = await collection.insert_one(interaction.dict())
            logger.info(f"시선 상호작용 저장 완료: {interaction.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"시선 상호작용 저장 실패: {e}")
            raise
    
    async def process_gaze_request(self, request: GazeDataRequest) -> GazeInteraction:
        """라즈베리파이 시선 데이터 요청을 GazeInteraction으로 변환"""
        try:
            # 기기별 시선 데이터 변환
            device_gaze_data = []
            total_duration = 0.0
            
            for device_id, probability in request.gaze_data.items():
                if probability > 0.1:  # 10% 이상 확률인 경우만 저장
                    gaze_data = DeviceGazeData(
                        device_id=device_id,
                        gaze_probability=probability,
                        duration=0.0,  # 실제 duration은 시간에 따라 계산
                        timestamp=request.timestamp
                    )
                    device_gaze_data.append(gaze_data)
                    total_duration += probability
            
            # GazeInteraction 생성
            interaction = GazeInteraction(
                user_id=request.user_id,
                session_id=request.session_id,
                device_gaze_data=device_gaze_data,
                total_duration=total_duration,
                time_context={
                    "timestamp": request.timestamp.isoformat(),
                    "hour": request.timestamp.hour,
                    "day_of_week": request.timestamp.weekday(),
                    "device_info": request.device_info,
                    "device_mapping": request.device_mapping
                }
            )
            
            logger.info(f"시선 데이터 요청 처리 완료: {request.session_id}")
            return interaction
            
        except Exception as e:
            logger.error(f"시선 데이터 요청 처리 실패: {e}")
            raise
    
    # 스마트 기기 관리
    async def save_smart_device(self, device: SmartDevice) -> str:
        """스마트 기기 저장"""
        try:
            collection = self._get_collection("smart_devices")
            result = await collection.insert_one(device.dict())
            logger.info(f"스마트 기기 저장 완료: {device.device_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"스마트 기기 저장 실패: {e}")
            raise
    
    async def get_user_devices(self, user_id: str) -> List[SmartDevice]:
        """사용자의 모든 스마트 기기 조회"""
        try:
            collection = self._get_collection("smart_devices")
            cursor = collection.find({"user_id": user_id, "is_active": True})
            devices = []
            async for doc in cursor:
                devices.append(SmartDevice(**doc))
            return devices
        except Exception as e:
            logger.error(f"사용자 기기 조회 실패: {e}")
            return []
    
    async def get_device_by_id(self, device_id: str, user_id: str) -> Optional[SmartDevice]:
        """특정 기기 조회"""
        try:
            collection = self._get_collection("smart_devices")
            data = await collection.find_one({
                "device_id": device_id, 
                "user_id": user_id, 
                "is_active": True
            })
            return SmartDevice(**data) if data else None
        except Exception as e:
            logger.error(f"기기 조회 실패: {e}")
            return None
    
    async def update_device_state(self, device_id: str, user_id: str, new_state: Dict[str, Any]) -> bool:
        """기기 상태 업데이트"""
        try:
            collection = self._get_collection("smart_devices")
            result = await collection.update_one(
                {"device_id": device_id, "user_id": user_id},
                {
                    "$set": {
                        "current_state": new_state,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"기기 상태 업데이트 실패: {e}")
            return False
    
    # 사용자 기기 레이아웃 관리
    async def save_device_layout(self, layout: UserDeviceLayout) -> str:
        """기기 레이아웃 저장"""
        try:
            collection = self._get_collection("user_device_layouts")
            result = await collection.insert_one(layout.dict())
            logger.info(f"기기 레이아웃 저장 완료: {layout.layout_name}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"기기 레이아웃 저장 실패: {e}")
            raise
    
    async def get_user_default_layout(self, user_id: str) -> Optional[UserDeviceLayout]:
        """사용자의 기본 레이아웃 조회"""
        try:
            collection = self._get_collection("user_device_layouts")
            data = await collection.find_one({
                "user_id": user_id, 
                "is_default": True
            })
            return UserDeviceLayout(**data) if data else None
        except Exception as e:
            logger.error(f"기본 레이아웃 조회 실패: {e}")
            return None
    
    async def get_user_layouts(self, user_id: str) -> List[UserDeviceLayout]:
        """사용자의 모든 레이아웃 조회"""
        try:
            collection = self._get_collection("user_device_layouts")
            cursor = collection.find({"user_id": user_id})
            layouts = []
            async for doc in cursor:
                layouts.append(UserDeviceLayout(**doc))
            return layouts
        except Exception as e:
            logger.error(f"사용자 레이아웃 조회 실패: {e}")
            return []
    
    async def get_gaze_interaction(self, interaction_id: str) -> Optional[GazeInteraction]:
        """시선 상호작용 조회"""
        try:
            collection = self._get_collection("gaze_interactions")
            data = await collection.find_one({"id": interaction_id})
            return GazeInteraction(**data) if data else None
        except Exception as e:
            logger.error(f"시선 상호작용 조회 실패: {e}")
            return None
    
    # 에이전트 실행 관리
    async def save_agent_execution(self, execution: AgentExecution) -> str:
        """에이전트 실행 기록 저장"""
        try:
            collection = self._get_collection("agent_executions")
            result = await collection.insert_one(execution.dict())
            logger.info(f"에이전트 실행 기록 저장 완료: {execution.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"에이전트 실행 기록 저장 실패: {e}")
            raise
    
    async def get_agent_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """에이전트 실행 기록 조회"""
        try:
            collection = self._get_collection("agent_executions")
            data = await collection.find_one({"id": execution_id})
            return AgentExecution(**data) if data else None
        except Exception as e:
            logger.error(f"에이전트 실행 기록 조회 실패: {e}")
            return None
    
    # 에이전트 세션 관리
    async def save_agent_session(self, session: AgentSession) -> str:
        """에이전트 세션 저장"""
        try:
            collection = self._get_collection("agent_sessions")
            result = await collection.insert_one(session.dict())
            logger.info(f"에이전트 세션 저장 완료: {session.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"에이전트 세션 저장 실패: {e}")
            raise
    
    async def update_agent_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """에이전트 세션 업데이트"""
        try:
            collection = self._get_collection("agent_sessions")
            update_data["updated_at"] = datetime.now()
            result = await collection.update_one(
                {"id": session_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"에이전트 세션 업데이트 실패: {e}")
            return False
    
    async def get_agent_session(self, session_id: str) -> Optional[AgentSession]:
        """에이전트 세션 조회"""
        try:
            collection = self._get_collection("agent_sessions")
            data = await collection.find_one({"id": session_id})
            return AgentSession(**data) if data else None
        except Exception as e:
            logger.error(f"에이전트 세션 조회 실패: {e}")
            return None
    
    # 사용자 피드백 관리
    async def save_user_feedback(self, feedback: UserFeedback) -> str:
        """사용자 피드백 저장"""
        try:
            collection = self._get_collection("user_feedback")
            result = await collection.insert_one(feedback.dict())
            logger.info(f"사용자 피드백 저장 완료: {feedback.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"사용자 피드백 저장 실패: {e}")
            raise
    
    async def get_user_feedback_by_session(self, session_id: str) -> List[UserFeedback]:
        """세션별 사용자 피드백 조회"""
        try:
            collection = self._get_collection("user_feedback")
            cursor = collection.find({"session_id": session_id})
            feedbacks = []
            async for doc in cursor:
                feedbacks.append(UserFeedback(**doc))
            return feedbacks
        except Exception as e:
            logger.error(f"사용자 피드백 조회 실패: {e}")
            return []
    
    # 추천 관리
    async def save_recommendation(self, recommendation: Recommendation) -> str:
        """추천 저장"""
        try:
            collection = self._get_collection("recommendations")
            result = await collection.insert_one(recommendation.dict())
            logger.info(f"추천 저장 완료: {recommendation.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"추천 저장 실패: {e}")
            raise
    
    async def update_recommendation_feedback(self, recommendation_id: str, is_accepted: bool, feedback_id: str) -> bool:
        """추천 피드백 업데이트"""
        try:
            collection = self._get_collection("recommendations")
            result = await collection.update_one(
                {"id": recommendation_id},
                {
                    "$set": {
                        "is_accepted": is_accepted,
                        "feedback_id": feedback_id,
                        "responded_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"추천 피드백 업데이트 실패: {e}")
            return False
    
    # 사용자 선호도 관리
    async def get_user_preference(self, user_id: str) -> Optional[UserPreference]:
        """사용자 선호도 조회"""
        try:
            collection = self._get_collection("user_preferences")
            data = await collection.find_one({"user_id": user_id})
            return UserPreference(**data) if data else None
        except Exception as e:
            logger.error(f"사용자 선호도 조회 실패: {e}")
            return None
    
    async def save_user_preference(self, preference: UserPreference) -> str:
        """사용자 선호도 저장/업데이트"""
        try:
            collection = self._get_collection("user_preferences")
            preference.last_updated = datetime.now()
            
            result = await collection.replace_one(
                {"user_id": preference.user_id},
                preference.dict(),
                upsert=True
            )
            logger.info(f"사용자 선호도 저장 완료: {preference.user_id}")
            return preference.id
        except Exception as e:
            logger.error(f"사용자 선호도 저장 실패: {e}")
            raise
    
    # 환경 데이터 관리
    async def save_environmental_data(self, env_data: EnvironmentalData) -> str:
        """환경 데이터 저장"""
        try:
            collection = self._get_collection("environmental_data")
            result = await collection.insert_one(env_data.dict())
            logger.info(f"환경 데이터 저장 완료: {env_data.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"환경 데이터 저장 실패: {e}")
            raise
    
    async def get_latest_environmental_data(self, hours: int = 1) -> Optional[EnvironmentalData]:
        """최신 환경 데이터 조회"""
        try:
            collection = self._get_collection("environmental_data")
            since = datetime.now() - timedelta(hours=hours)
            data = await collection.find_one(
                {"timestamp": {"$gte": since}},
                sort=[("timestamp", -1)]
            )
            return EnvironmentalData(**data) if data else None
        except Exception as e:
            logger.error(f"환경 데이터 조회 실패: {e}")
            return None
    
    # 시스템 메트릭 관리
    async def save_system_metrics(self, metrics: SystemMetrics) -> str:
        """시스템 메트릭 저장"""
        try:
            collection = self._get_collection("system_metrics")
            result = await collection.insert_one(metrics.dict())
            logger.info(f"시스템 메트릭 저장 완료: {metrics.id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"시스템 메트릭 저장 실패: {e}")
            raise
    
    async def get_agent_performance_stats(self, agent_type: AgentType, hours: int = 24) -> Dict[str, Any]:
        """에이전트 성능 통계 조회"""
        try:
            collection = self._get_collection("system_metrics")
            since = datetime.now() - timedelta(hours=hours)
            
            pipeline = [
                {
                    "$match": {
                        "agent_type": agent_type.value,
                        "timestamp": {"$gte": since}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_execution_time": {"$avg": "$execution_time_avg_ms"},
                        "avg_success_rate": {"$avg": "$success_rate"},
                        "total_api_calls": {"$sum": "$gemini_api_calls_count"},
                        "avg_error_rate": {"$avg": "$error_rate"},
                        "avg_satisfaction": {"$avg": "$user_satisfaction_score"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"에이전트 성능 통계 조회 실패: {e}")
            return {}


# 전역 MongoDB 서비스 인스턴스
mongodb_service = MongoDBService()
