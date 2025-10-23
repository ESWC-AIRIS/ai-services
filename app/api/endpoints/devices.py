"""
GazeHome AI Services - LG Control Endpoints
LG 스마트기기 제어 관련 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging
import httpx
from app.core.config import *

router = APIRouter()
logger = logging.getLogger(__name__)


class LGControlRequest(BaseModel):
    """LG 스마트기기 제어 요청 (명세서)"""
    device_id: str = Field(..., description="기기 ID (예: b403...)")
    action: str = Field(..., description="제어 액션 (turn_on/turn_off/clean/auto 중 하나)")


class LGControlResponse(BaseModel):
    """LG 스마트기기 제어 응답 (명세서)"""
    message: str


class GatewayClient:
    """Gateway 통신 클라이언트"""
    
    def __init__(self, gateway_endpoint: str = GATEWAY_ENDPOINT):
        self.gateway_endpoint = gateway_endpoint
        self.timeout = 10.0
        logger.info(f"GatewayClient 초기화: endpoint={self.gateway_endpoint}")
    
    async def control_device(self, device_id: str, action: str) -> Dict[str, Any]:
        """Gateway를 통해 LG 기기 제어"""
        try:
            payload = {
                "device_id": device_id,
                "action": action
            }
            
            logger.info(f"🚀 Gateway로 기기 제어 요청:")
            logger.info(f"  - 기기: {device_id}")
            logger.info(f"  - 액션: {action}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.gateway_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Gateway 제어 성공: {result.get('message')}")
                    return result
                else:
                    logger.error(f"❌ Gateway 제어 실패: status={response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Gateway 제어 실패: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Gateway 통신 타임아웃: device_id={device_id}")
            raise HTTPException(status_code=504, detail="Gateway 통신 타임아웃")
        except httpx.RequestError as e:
            logger.error(f"Gateway 통신 에러: {e}")
            raise HTTPException(status_code=503, detail=f"Gateway 통신 에러: {str(e)}")
        except Exception as e:
            logger.error(f"기기 제어 중 예외 발생: {e}")
            raise HTTPException(status_code=500, detail=f"기기 제어 실패: {str(e)}")


# Gateway 클라이언트 인스턴스
gateway_client = GatewayClient()


@router.post("/control", response_model=LGControlResponse)
async def control_lg_device(request: LGControlRequest):
    """
    HW → AI: 스마트기기 단순 제어 (명세서)
    AI → Gateway: LG Thinq 조작 (명세서)
    
    하드웨어에서 직접 제어 요청이 오면 AI가 처리 후 Gateway로 전달합니다.
    """
    try:
        # 액션 유효성 검사
        valid_actions = ["turn_on", "turn_off", "clean", "auto", "dryer_on", "dryer_off"]
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 액션입니다. 가능한 액션: {valid_actions}"
            )
        
        logger.info(f"📱 HW → AI 제어 요청 수신:")
        logger.info(f"  - 기기: {request.device_id}")
        logger.info(f"  - 액션: {request.action}")
        
        # Gateway로 제어 요청 전달
        gateway_result = await gateway_client.control_device(
            device_id=request.device_id,
            action=request.action
        )
        
        return LGControlResponse(
            message="[AI] 스마트 기기 단순 제어 완료"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LG 기기 제어 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LG 기기 제어 실패: {str(e)}"
        )