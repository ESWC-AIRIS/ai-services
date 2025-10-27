"""
GazeHome AI Services - Recommendation Service
MongoDB 추천 관리 서비스
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timedelta
import logging

from app.models.recommendations import (
    Recommendation, RecommendationStatus, DeviceControl,
    generate_recommendation_id
)
from app.core.database import get_database

logger = logging.getLogger(__name__)


class RecommendationService:
    """추천 관리 서비스"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.recommendations
    
    async def create_recommendation(
        self, 
        title: str, 
        contents: str, 
        context: Optional[str] = None,
        device_control: Optional[DeviceControl] = None
    ) -> Recommendation:
        """새 추천 생성"""
        try:
            recommendation_id = generate_recommendation_id()
            
            recommendation = Recommendation(
                recommendation_id=recommendation_id,
                title=title,
                contents=contents,
                context=context,
                device_control=device_control,
                status=RecommendationStatus.PENDING
            )
            
            result = await self.collection.insert_one(recommendation.dict(by_alias=True))
            
            if result.inserted_id:
                logger.info(f"✅ 추천 생성 완료: {recommendation_id}")
                return recommendation
            else:
                raise Exception("추천 생성 실패")
                
        except Exception as e:
            logger.error(f"❌ 추천 생성 실패: {e}")
            raise
    
    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[Recommendation]:
        """추천 ID로 추천 조회"""
        try:
            doc = await self.collection.find_one({"recommendation_id": recommendation_id})
            
            if doc:
                return Recommendation(**doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ 추천 조회 실패: {e}")
            return None
    
    async def confirm_recommendation(
        self, 
        recommendation_id: str, 
        user_response: str
    ) -> Optional[Recommendation]:
        """추천 확인 처리"""
        try:
            # 추천 조회
            recommendation = await self.get_recommendation_by_id(recommendation_id)
            
            if not recommendation:
                logger.warning(f"❌ 추천을 찾을 수 없음: {recommendation_id}")
                return None
            
            # 상태 업데이트
            status = RecommendationStatus.CONFIRMED if user_response.upper() == "YES" else RecommendationStatus.REJECTED
            
            update_data = {
                "status": status,
                "user_response": user_response.upper(),
                "confirmed_at": datetime.utcnow()
            }
            
            result = await self.collection.update_one(
                {"recommendation_id": recommendation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ 추천 확인 처리 완료: {recommendation_id} -> {status}")
                
                # 업데이트된 추천 반환
                updated_doc = await self.collection.find_one({"recommendation_id": recommendation_id})
                return Recommendation(**updated_doc)
            else:
                logger.warning(f"❌ 추천 확인 처리 실패: {recommendation_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 추천 확인 처리 실패: {e}")
            return None
    
    async def mark_hardware_sent(self, recommendation_id: str) -> bool:
        """하드웨어 전송 완료 표시"""
        try:
            result = await self.collection.update_one(
                {"recommendation_id": recommendation_id},
                {"$set": {"hardware_sent_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ 하드웨어 전송 완료 표시: {recommendation_id}")
                return True
            else:
                logger.warning(f"❌ 하드웨어 전송 표시 실패: {recommendation_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 하드웨어 전송 표시 실패: {e}")
            return False
    
    async def get_recommendations_by_status(
        self, 
        status: RecommendationStatus,
        limit: int = 10,
        skip: int = 0
    ) -> List[Recommendation]:
        """상태별 추천 목록 조회"""
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", -1).skip(skip).limit(limit)
            
            recommendations = []
            async for doc in cursor:
                recommendations.append(Recommendation(**doc))
            
            logger.info(f"✅ 상태별 추천 조회 완료: {status} ({len(recommendations)}개)")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ 상태별 추천 조회 실패: {e}")
            return []
    
    async def get_pending_recommendations(self, limit: int = 10) -> List[Recommendation]:
        """대기중인 추천 목록 조회"""
        return await self.get_recommendations_by_status(RecommendationStatus.PENDING, limit)
    
    async def get_recommendation_statistics(self) -> Dict[str, Any]:
        """추천 통계 조회"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            stats = {}
            async for doc in self.collection.aggregate(pipeline):
                stats[doc["_id"]] = doc["count"]
            
            # 전체 개수
            total_count = await self.collection.count_documents({})
            
            return {
                "total_recommendations": total_count,
                "by_status": stats,
                "pending_count": stats.get(RecommendationStatus.PENDING, 0),
                "confirmed_count": stats.get(RecommendationStatus.CONFIRMED, 0),
                "rejected_count": stats.get(RecommendationStatus.REJECTED, 0)
            }
            
        except Exception as e:
            logger.error(f"❌ 추천 통계 조회 실패: {e}")
            return {}
    
    async def cleanup_expired_recommendations(self, hours: int = 24) -> int:
        """만료된 추천 정리 (24시간 이상 대기중인 것들)"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = await self.collection.update_many(
                {
                    "status": RecommendationStatus.PENDING,
                    "created_at": {"$lt": cutoff_time}
                },
                {"$set": {"status": RecommendationStatus.EXPIRED}}
            )
            
            logger.info(f"✅ 만료된 추천 정리 완료: {result.modified_count}개")
            return result.modified_count
            
        except Exception as e:
            logger.error(f"❌ 만료된 추천 정리 실패: {e}")
            return 0


# 전역 서비스 인스턴스
_recommendation_service: Optional[RecommendationService] = None


async def get_recommendation_service() -> RecommendationService:
    """추천 서비스 인스턴스 반환"""
    global _recommendation_service
    
    if _recommendation_service is None:
        db = await get_database()
        _recommendation_service = RecommendationService(db)
    
    return _recommendation_service
