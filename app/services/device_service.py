"""
GazeHome AI Services - Device Management Service
MongoDB 기기 관리 서비스
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URL, MONGODB_DATABASE
from app.models.device_management import UserDevice, DeviceType, DeviceRegistrationRequest

logger = logging.getLogger(__name__)


class DeviceService:
    """기기 관리 서비스"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
    
    async def connect(self):
        """MongoDB 연결"""
        try:
            if MONGODB_URL:
                self.client = AsyncIOMotorClient(MONGODB_URL)
                self.database = self.client[MONGODB_DATABASE or "gazehome"]
                self.collection = self.database["user_devices"]
                logger.info("MongoDB 연결 성공")
            else:
                logger.warning("MONGODB_URL이 설정되지 않음. 메모리 모드로 동작")
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """MongoDB 연결 해제"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 해제")
    
    async def register_device(self, user_id: str, device_data: DeviceRegistrationRequest) -> UserDevice:
        """기기 등록"""
        try:
            # 중복 기기 확인
            existing_device = await self.collection.find_one({
                "user_id": user_id,
                "device_id": device_data.device_id
            })
            
            if existing_device:
                raise ValueError(f"기기 {device_data.device_id}가 이미 등록되어 있습니다")
            
            # 새 기기 생성
            device = UserDevice(
                user_id=user_id,
                device_id=device_data.device_id,
                device_type=device_data.device_type,
                alias=device_data.alias,
                supported_actions=device_data.supported_actions
            )
            
            # MongoDB에 저장
            result = await self.collection.insert_one(device.dict(by_alias=True))
            device.id = result.inserted_id
            
            logger.info(f"기기 등록 완료: {device_data.device_id}")
            return device
            
        except Exception as e:
            logger.error(f"기기 등록 실패: {e}")
            raise
    
    async def get_user_devices(self, user_id: str) -> List[UserDevice]:
        """사용자 기기 목록 조회"""
        try:
            cursor = self.collection.find({"user_id": user_id, "is_active": True})
            devices = []
            
            async for doc in cursor:
                device = UserDevice(**doc)
                devices.append(device)
            
            logger.info(f"사용자 {user_id}의 기기 {len(devices)}개 조회")
            return devices
            
        except Exception as e:
            logger.error(f"기기 목록 조회 실패: {e}")
            raise
    
    async def get_device_by_id(self, user_id: str, device_id: str) -> Optional[UserDevice]:
        """특정 기기 조회"""
        try:
            doc = await self.collection.find_one({
                "user_id": user_id,
                "device_id": device_id,
                "is_active": True
            })
            
            if doc:
                return UserDevice(**doc)
            return None
            
        except Exception as e:
            logger.error(f"기기 조회 실패: {e}")
            raise
    
    async def update_device(self, user_id: str, device_id: str, update_data: Dict[str, Any]) -> Optional[UserDevice]:
        """기기 정보 업데이트"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"user_id": user_id, "device_id": device_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_device_by_id(user_id, device_id)
            return None
            
        except Exception as e:
            logger.error(f"기기 업데이트 실패: {e}")
            raise
    
    async def deactivate_device(self, user_id: str, device_id: str) -> bool:
        """기기 비활성화"""
        try:
            result = await self.collection.update_one(
                {"user_id": user_id, "device_id": device_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"기기 비활성화 실패: {e}")
            raise


# 기기 타입별 지원 액션 매핑
DEVICE_ACTIONS = {
    DeviceType.AIR_PURIFIER: ["turn_on", "turn_off", "clean", "auto"],
    DeviceType.AIR_CONDITIONER: ["aircon_on", "aircon_off"] + [f"temp_{i}" for i in range(18, 31)]
}


def get_supported_actions(device_type: DeviceType) -> List[str]:
    """기기 타입별 지원 액션 반환"""
    return DEVICE_ACTIONS.get(device_type, [])


# 전역 서비스 인스턴스
device_service = DeviceService()
