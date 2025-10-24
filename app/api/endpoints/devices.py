"""
GazeHome AI Services - LG Control Endpoints
LG 스마트기기 제어 관련 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import httpx
from app.core.config import *
from app.models.lg_control import LGControlRequest, LGControlResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# 모델들은 app.models.lg_control에서 import


class GatewayClient:
    """Gateway 통신 클라이언트"""
    
    def __init__(self, gateway_url: str = GATEWAY_URL):
        self.gateway_url = gateway_url
        self.control_endpoint = GATEWAY_CONTROL_ENDPOINT
        self.devices_endpoint = GATEWAY_DEVICES_ENDPOINT
        self.timeout = 10.0
        logger.info(f"GatewayClient 초기화: url={self.gateway_url}")
    
    async def get_available_devices(self) -> Dict[str, Any]:
        """Gateway에서 사용 가능한 기기 목록 조회"""
        try:
            logger.info("🔍 Gateway에서 기기 목록 조회 중...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.devices_endpoint,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Gateway 기기 목록 조회 성공: {len(result.get('response', []))}개 기기")
                    return result
                else:
                    logger.error(f"❌ Gateway 기기 목록 조회 실패: status={response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Gateway 기기 목록 조회 실패: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Gateway 기기 목록 조회 타임아웃")
            raise HTTPException(status_code=504, detail="Gateway 통신 타임아웃")
        except httpx.RequestError as e:
            logger.error(f"Gateway 통신 에러: {e}")
            raise HTTPException(status_code=503, detail=f"Gateway 통신 에러: {str(e)}")
        except Exception as e:
            logger.error(f"기기 목록 조회 중 예외 발생: {e}")
            raise HTTPException(status_code=500, detail=f"기기 목록 조회 실패: {str(e)}")
    
    async def get_device_profile(self, device_id: str) -> Dict[str, Any]:
        """Gateway에서 특정 기기의 상세 정보 조회"""
        try:
            profile_endpoint = f"{self.devices_endpoint}/{device_id}/profile"
            logger.info(f"🔍 Gateway에서 기기 프로필 조회: {device_id}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    profile_endpoint,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Gateway 기기 프로필 조회 성공: {device_id}")
                    return result
                else:
                    logger.error(f"❌ Gateway 기기 프로필 조회 실패: status={response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Gateway 기기 프로필 조회 실패: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Gateway 기기 프로필 조회 타임아웃: {device_id}")
            raise HTTPException(status_code=504, detail="Gateway 통신 타임아웃")
        except httpx.RequestError as e:
            logger.error(f"Gateway 통신 에러: {e}")
            raise HTTPException(status_code=503, detail=f"Gateway 통신 에러: {str(e)}")
        except Exception as e:
            logger.error(f"기기 프로필 조회 중 예외 발생: {e}")
            raise HTTPException(status_code=500, detail=f"기기 프로필 조회 실패: {str(e)}")
    
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
                    self.control_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Gateway 응답에서 message 또는 error 필드 확인
                    response_message = result.get('message') or result.get('error', '제어 완료')
                    logger.info(f"✅ Gateway 제어 성공: {response_message}")
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


# 명세서에 없는 엔드포인트들은 삭제하고, 기존 control 엔드포인트만 유지


@router.post("/control", response_model=LGControlResponse)
async def control_lg_device(request: LGControlRequest):
    """
    AI → Gateway: LG Thinq 조작 (명세서)
    
    AI가 Gateway를 통해 LG 기기를 제어합니다.
    """
    try:
        logger.info(f"🚀 AI → Gateway 기기 제어 요청:")
        logger.info(f"  - 기기: {request.device_id}")
        logger.info(f"  - 액션: {request.action}")
        
        # Gateway에서 실제 기기 목록 조회하여 유효성 검사
        try:
            gateway_devices = await gateway_client.get_available_devices()
            available_device_ids = [device["deviceId"] for device in gateway_devices.get("response", [])]
            
            if request.device_id not in available_device_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"기기 {request.device_id}가 Gateway에서 찾을 수 없습니다. 사용 가능한 기기: {available_device_ids}"
                )
            
            logger.info(f"✅ 기기 {request.device_id}가 Gateway에서 확인됨")
            
        except HTTPException as e:
            if e.status_code == 404:
                raise e
            # Gateway 통신 실패 시에도 제어는 시도 (Gateway가 일시적으로 다운될 수 있음)
            logger.warning(f"Gateway 기기 목록 조회 실패, 제어 시도: {e.detail}")
        
        # Gateway로 제어 요청 전달
        gateway_result = await gateway_client.control_device(
            device_id=request.device_id,
            action=request.action
        )
        
        # 기기별 응답 메시지 생성
        if "air_purifier" in request.device_id.lower() or "air" in request.device_id.lower():
            message = "[GATEWAY] 스마트 기기(공기청정기) 제어 완료"
        elif "dryer" in request.device_id.lower() or "dry" in request.device_id.lower():
            message = "[GATEWAY] 스마트 기기 제어(건조기) 완료"
        elif "air_conditioner" in request.device_id.lower() or "ac" in request.device_id.lower():
            message = "[GATEWAY] 스마트 기기 제어(에어컨) 완료"
        elif "washer" in request.device_id.lower():
            message = "[GATEWAY] 스마트 기기 제어(세탁기) 완료"
        else:
            message = "[GATEWAY] 스마트 기기 제어 완료"
        
        return LGControlResponse(message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LG 기기 제어 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"LG 기기 제어 실패: {str(e)}"
        )