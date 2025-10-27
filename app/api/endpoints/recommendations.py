"""
GazeHome AI Services - Recommendations Endpoints
AI → HW 추천 시스템 API 엔드포인트 (새로운 명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
import httpx
from app.core.config import *
from app.models.recommendations import (
    RecommendationCreateRequest, RecommendationCreateResponse,
    RecommendationConfirmRequest, RecommendationConfirmResponse,
    DeviceControl
)
from app.services.recommendation_service import get_recommendation_service

router = APIRouter()
logger = logging.getLogger(__name__)


class HardwareClient:
    """하드웨어 통신 클라이언트"""
    
    def __init__(self, hardware_url: str = HARDWARE_URL):
        self.hardware_url = hardware_url
        self.recommendations_endpoint = HARDWARE_RECOMMENDATIONS_ENDPOINT
        self.timeout = 10.0
        logger.info(f"HardwareClient 초기화: url={self.hardware_url}")
    
    async def send_recommendation(self, recommendation_id: str, title: str, contents: str) -> Dict[str, Any]:
        """하드웨어로 추천 전송"""
        try:
            payload = {
                "recommendation_id": recommendation_id,
                "title": title,
                "contents": contents
            }
            
            logger.info(f"🚀 하드웨어로 추천 전송:")
            logger.info(f"  - ID: {recommendation_id}")
            logger.info(f"  - 제목: \"{title}\"")
            logger.info(f"  - 내용: \"{contents}\"")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.recommendations_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ 하드웨어 응답 수신: {result}")
                    return result
                else:
                    logger.warning(f"⚠️ 하드웨어 응답 오류: {response.status_code}")
                    return {
                        "message": f"하드웨어 응답 오류: {response.status_code}",
                        "confirm": "PENDING"
                    }
                    
        except httpx.ConnectError:
            logger.warning(f"❌ 하드웨어 서버 연결 실패: {self.hardware_url}")
            return {
                "message": "하드웨어 서버 연결 실패",
                "confirm": "PENDING"
            }
        except Exception as e:
            logger.error(f"❌ 하드웨어 통신 실패: {e}")
            return {
                "message": f"하드웨어 통신 실패: {str(e)}",
                "confirm": "PENDING"
            }


# 하드웨어 클라이언트 인스턴스
hardware_client = HardwareClient()


@router.post("/", response_model=RecommendationCreateResponse)
async def create_recommendation(request: RecommendationCreateRequest):
    """AI → HW 추천 생성 및 전송"""
    try:
        # 추천 서비스 가져오기
        recommendation_service = await get_recommendation_service()
        
        # AI Agent로 추천 생성
        from app.agents.recommendation_agent import create_agent
        agent = create_agent()
        
        # Agent로 추천 생성
        agent_recommendation = await agent.generate_recommendation(request.context)
        
        # 기기 제어 정보 추출
        device_control = None
        if agent_recommendation.get('device_control'):
            control_info = agent_recommendation['device_control']
            device_control = DeviceControl(
                device_type=control_info.get('device_type'),
                action=control_info.get('action'),
                device_id=control_info.get('device_id')
            )
        
        # MongoDB에 추천 저장
        recommendation = await recommendation_service.create_recommendation(
            title=request.title,
            contents=request.contents,
            context=request.context,
            device_control=device_control
        )
        
        # 하드웨어에 추천 전송
        hardware_response = await hardware_client.send_recommendation(
            recommendation.recommendation_id,
            request.title,
            request.contents
        )
        
        # 하드웨어 전송 완료 표시
        await recommendation_service.mark_hardware_sent(recommendation.recommendation_id)
        
        logger.info(f"✅ 추천 생성 및 하드웨어 전송 완료: {recommendation.recommendation_id}")
        
        return RecommendationCreateResponse(
            recommendation_id=recommendation.recommendation_id,
            message="추천이 하드웨어에 전송되었습니다"
        )
        
    except Exception as e:
        logger.error(f"❌ 추천 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"추천 생성 실패: {str(e)}")


@router.post("/confirm", response_model=RecommendationConfirmResponse)
async def confirm_recommendation(request: RecommendationConfirmRequest):
    """HW → AI 사용자 응답 처리"""
    try:
        # 추천 서비스 가져오기
        recommendation_service = await get_recommendation_service()
        
        # 추천 확인 처리
        updated_recommendation = await recommendation_service.confirm_recommendation(
            request.recommendation_id,
            request.confirm
        )
        
        if not updated_recommendation:
            raise HTTPException(status_code=404, detail="추천을 찾을 수 없습니다")
        
        # 사용자가 YES로 응답한 경우 기기 제어 실행
        if request.confirm.upper() == "YES" and updated_recommendation.device_control:
            try:
                # Gateway API로 기기 제어 (기존 GatewayClient 사용)
                from app.api.endpoints.devices import gateway_client
                
                control_result = await gateway_client.control_device(
                    device_id=updated_recommendation.device_control.device_id,
                    action=updated_recommendation.device_control.action
                )
                
                logger.info(f"✅ 기기 제어 실행 완료: {control_result}")
                
            except Exception as e:
                logger.warning(f"⚠️ 기기 제어 실행 실패: {e}")
        
        logger.info(f"✅ 사용자 응답 처리 완료: {request.recommendation_id} -> {request.confirm}")
        
        return RecommendationConfirmResponse(
            recommendation_id=request.recommendation_id,
            message="추천이 AI에 전송되었습니다"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사용자 응답 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"사용자 응답 처리 실패: {str(e)}")