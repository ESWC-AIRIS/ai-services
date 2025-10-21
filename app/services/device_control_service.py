"""
GazeHome AI Services - Device Control Service
IoT 기기 직접 제어 서비스
"""

import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeviceControlService:
    """
    IoT 기기 제어 서비스
    
    AI 서비스가 직접 IoT 기기를 제어합니다.
    """
    
    def __init__(self, iot_api_endpoint: Optional[str] = None):
        """
        초기화
        
        Args:
            iot_api_endpoint: IoT 기기 제어 API 엔드포인트
        """
        self.iot_api_endpoint = iot_api_endpoint or getattr(
            settings,
            'IOT_API_ENDPOINT',
            'http://localhost:8080/api/devices'  # 기본값
        )
        self.timeout = 10.0
        logger.info(f"DeviceControlService 초기화: endpoint={self.iot_api_endpoint}")
    
    async def execute_device_command(
        self,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        IoT 기기 제어 명령 실행
        
        Args:
            device_id: 기기 ID (예: "light_living_room")
            command: 명령어 (예: "turn_on", "turn_off", "set_temperature")
            parameters: 추가 파라미터 (예: {"brightness": 70})
            
        Returns:
            실행 성공 여부
        """
        try:
            payload = {
                "device_id": device_id,
                "command": command,
                "parameters": parameters or {}
            }
            
            logger.info(f"🎮 기기 제어 실행:")
            logger.info(f"  - 기기: {device_id}")
            logger.info(f"  - 명령어: {command}")
            logger.info(f"  - 파라미터: {parameters}")
            
            url = f"{self.iot_api_endpoint}/{device_id}/control"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ 성공: {device_id} 제어 완료")
                    return True
                else:
                    logger.warning(
                        f"⚠️ 실패: status={response.status_code}, "
                        f"response={response.text}"
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"기기 제어 타임아웃: {device_id}")
            return False
        except httpx.RequestError as e:
            logger.error(f"기기 제어 통신 에러: {e}")
            return False
        except Exception as e:
            logger.error(f"기기 제어 중 예외 발생: {e}")
            return False
    
    async def execute_recommendation_action(
        self,
        recommendation: Dict[str, Any]
    ) -> bool:
        """
        추천 액션 실행
        
        Args:
            recommendation: 추천 정보 (device_id, action 포함)
            
        Returns:
            실행 성공 여부
        """
        device_id = recommendation.get('device_id')
        action = recommendation.get('action', {})
        command = action.get('command')
        parameters = action.get('parameters', {})
        
        if not device_id or not command:
            logger.error(f"잘못된 추천 정보: device_id 또는 command 없음")
            return False
        
        return await self.execute_device_command(
            device_id=device_id,
            command=command,
            parameters=parameters
        )


# 싱글톤 인스턴스
_device_control_service: Optional[DeviceControlService] = None


def get_device_control_service(endpoint: Optional[str] = None) -> DeviceControlService:
    """DeviceControlService 싱글톤 인스턴스 반환"""
    global _device_control_service
    if _device_control_service is None:
        _device_control_service = DeviceControlService(endpoint)
    return _device_control_service

