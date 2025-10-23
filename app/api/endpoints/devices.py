"""
GazeHome AI Services - LG Control Endpoints
LG 스마트기기 제어 관련 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import logging
import httpx
from app.core.config import *
from app.models.device_management import (
    DeviceRegistrationRequest, DeviceRegistrationResponse, 
    DeviceListResponse, DeviceType, get_supported_actions
)
from app.services.device_service import device_service

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


@router.post("/register", response_model=DeviceRegistrationResponse)
async def register_device(request: DeviceRegistrationRequest):
    """
    기기 등록 API
    사용자의 기기를 시스템에 등록합니다.
    """
    try:
        # 기본 사용자 ID (MVP에서는 단일 사용자)
        user_id = "default_user"
        
        # 기기 등록
        device = await device_service.register_device(user_id, request)
        
        logger.info(f"기기 등록 완료: {device.device_id}")
        
        return DeviceRegistrationResponse(
            message="기기 등록이 완료되었습니다",
            device_id=device.device_id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"기기 등록 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"기기 등록 실패: {str(e)}"
        )


@router.get("/devices", response_model=DeviceListResponse)
async def get_user_devices():
    """
    사용자 기기 목록 조회 API
    등록된 모든 기기를 조회합니다.
    """
    try:
        # 기본 사용자 ID (MVP에서는 단일 사용자)
        user_id = "default_user"
        
        # 기기 목록 조회
        devices = await device_service.get_user_devices(user_id)
        
        logger.info(f"기기 목록 조회: {len(devices)}개")
        
        return DeviceListResponse(devices=devices)
        
    except Exception as e:
        logger.error(f"기기 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"기기 목록 조회 실패: {str(e)}"
        )


@router.post("/control", response_model=LGControlResponse)
async def control_lg_device(request: LGControlRequest):
    """
    AI → Gateway: LG Thinq 조작 (명세서)
    
    AI가 Gateway를 통해 LG 기기를 제어합니다.
    """
    try:
        # 기본 사용자 ID (MVP에서는 단일 사용자)
        user_id = "default_user"
        
        # 등록된 기기인지 확인
        device = await device_service.get_device_by_id(user_id, request.device_id)
        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"기기 {request.device_id}를 찾을 수 없습니다"
            )
        
        # 액션 유효성 검사
        if request.action not in device.supported_actions:
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 액션입니다. 가능한 액션: {device.supported_actions}"
            )
        
        logger.info(f"🚀 AI → Gateway 기기 제어:")
        logger.info(f"  - 기기: {request.device_id} ({device.alias})")
        logger.info(f"  - 액션: {request.action}")
        
        # Gateway로 제어 요청 전달
        gateway_result = await gateway_client.control_device(
            device_id=request.device_id,
            action=request.action
        )
        
        return LGControlResponse(
            message="[GATEWAY] 스마트 기기 제어 완료"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LG 기기 제어 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LG 기기 제어 실패: {str(e)}"
        )