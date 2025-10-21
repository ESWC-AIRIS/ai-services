"""
GazeHome AI Services - Hardware Client
하드웨어로 추천을 전송하는 클라이언트
"""

import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class HardwareClient:
    """
    하드웨어 클라이언트
    
    AI 서비스에서 하드웨어로 능동적 추천을 전송합니다.
    """
    
    def __init__(self, hardware_endpoint: Optional[str] = None):
        """
        클라이언트 초기화
        
        Args:
            hardware_endpoint: 하드웨어 엔드포인트 URL
                              None이면 settings에서 가져옴
        """
        self.hardware_endpoint = hardware_endpoint or getattr(
            settings, 
            'HARDWARE_ENDPOINT', 
            'http://localhost:8080/api/recommendations'  # 기본값
        )
        self.timeout = 10.0  # 10초 타임아웃
        logger.info(f"HardwareClient 초기화: endpoint={self.hardware_endpoint}")
    
    async def send_recommendation(
        self, 
        user_id: str, 
        recommendation: Dict[str, Any]
    ) -> bool:
        """
        하드웨어로 추천 전송
        
        Args:
            user_id: 사용자 ID
            recommendation: 추천 정보
            
        Returns:
            전송 성공 여부
        """
        try:
            payload = {
                "user_id": user_id,
                "recommendation": recommendation,
                "timestamp": recommendation.get('timestamp'),
                "type": "proactive"
            }
            
            logger.info(f"🚀 하드웨어로 추천 전송 시작:")
            logger.info(f"  - 사용자: {user_id}")
            logger.info(f"  - 추천 문구: \"{recommendation.get('prompt_text')}\"")
            logger.info(f"  - 기기: {recommendation.get('device_name')} ({recommendation.get('device_id')})")
            logger.info(f"  - 명령어: {recommendation.get('action')}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.hardware_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ 추천 전송 성공: user_id={user_id}")
                    return True
                else:
                    logger.warning(
                        f"⚠️ 추천 전송 실패: status={response.status_code}, "
                        f"response={response.text}"
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"하드웨어 통신 타임아웃: user_id={user_id}")
            return False
        except httpx.RequestError as e:
            logger.error(f"하드웨어 통신 에러: {e}")
            return False
        except Exception as e:
            logger.error(f"추천 전송 중 예외 발생: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        하드웨어 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # 헬스체크 엔드포인트가 있다면 사용
                health_endpoint = self.hardware_endpoint.replace(
                    '/api/recommendations', 
                    '/health'
                )
                response = await client.get(health_endpoint)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"하드웨어 연결 테스트 실패: {e}")
            return False


# 싱글톤 인스턴스
_hardware_client: Optional[HardwareClient] = None


def get_hardware_client(endpoint: Optional[str] = None) -> HardwareClient:
    """HardwareClient 싱글톤 인스턴스 반환"""
    global _hardware_client
    if _hardware_client is None:
        _hardware_client = HardwareClient(endpoint)
    return _hardware_client

