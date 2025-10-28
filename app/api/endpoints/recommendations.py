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
    HardwareRecommendationRequest, DeviceControl
)
from app.services.recommendation_service import get_recommendation_service

router = APIRouter()
logger = logging.getLogger(__name__)


class HardwareClient:
    """하드웨어 통신 클라이언트"""
    
    def __init__(self, hardware_url: str = HARDWARE_URL):
        self.hardware_url = hardware_url
        self.recommendations_endpoint = HARDWARE_RECOMMENDATIONS_ENDPOINT
        self.timeout = 60.0
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
async def send_to_hardware(request: HardwareRecommendationRequest):
    """AI → HW 추천 전달 (명세서)"""
    try:
        logger.info(f"🤖 AI Agent로 추천 생성 및 하드웨어 전달:")
        logger.info(f"  - 사용자 ID: {request.user_id}")
        
        # AI Agent로 추천 생성 (운영 모드)
        from app.agents.recommendation_agent import RecommendationAgent
        
        agent = RecommendationAgent()
        ai_recommendation = await agent.generate_recommendation("운영 모드에서 스마트 홈 추천을 생성해주세요.")
        
        if not ai_recommendation or not ai_recommendation.get('device_control'):
            raise HTTPException(status_code=500, detail="AI 추천 생성에 실패했습니다.")
        
        # MongoDB에 추천 데이터 저장 (운영 모드)
        from app.core.database import get_database
        from app.services.recommendation_service import RecommendationService
        
        db = await get_database()
        recommendation_service = RecommendationService(db)
        
        # device_control 정보 추출 및 변환
        device_control_data = ai_recommendation.get('device_control', {})
        device_control = DeviceControl(**device_control_data) if device_control_data else None
        
        recommendation_id = await recommendation_service.create_recommendation(
            title=ai_recommendation['title'],
            contents=ai_recommendation['contents'],
            device_control=device_control,
            user_id=request.user_id,
            mode="production"
        )
        
        logger.info(f"✅ MongoDB에 추천 저장 완료: {recommendation_id}")
        
        # 하드웨어에 추천 전송
        hardware_response = await hardware_client.send_recommendation(
            recommendation_id,
            ai_recommendation['title'],
            ai_recommendation['contents']
        )
        
        logger.info(f"✅ 하드웨어 전송 완료: {hardware_response}")
        
        # 응답 반환
        return RecommendationCreateResponse(
            recommendation_id=recommendation_id,
            message="AI 추천이 하드웨어에 전송되었습니다"
        )
        
    except Exception as e:
        logger.error(f"❌ 하드웨어 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"하드웨어 전송 실패: {str(e)}")


@router.post("/generate", response_model=RecommendationCreateResponse)
async def create_demo_recommendation(request: RecommendationCreateRequest):
    """데모용 추천 생성 및 하드웨어 전송"""
    try:
        logger.info(f"🎯 데모 추천 생성 요청:")
        logger.info(f"  - 사용자 ID: {request.user_id}")
        logger.info(f"  - 시나리오: {request.scenario}")
        
        # 추천 서비스 가져오기
        recommendation_service = await get_recommendation_service()
        
        # 데모용 추천 생성 (시나리오 기반)
        from app.agents.recommendation_agent import demo_generate_recommendation
        ai_recommendation = await demo_generate_recommendation(request.scenario)
        
        if not ai_recommendation or not ai_recommendation.get('device_control'):
            raise HTTPException(status_code=500, detail="데모 추천 생성에 실패했습니다.")
        
        # 기기 제어 정보 추출
        device_control = DeviceControl(**ai_recommendation['device_control'])
        
        # MongoDB에 추천 데이터 저장 (데모 모드)
        recommendation_id = await recommendation_service.create_recommendation(
            title=ai_recommendation['title'],
            contents=ai_recommendation['contents'],
            device_control=device_control,
            user_id=request.user_id,
            mode="demo"
        )
        
        # 하드웨어에 추천 전송
        hardware_response = await hardware_client.send_recommendation(
            recommendation_id,
            ai_recommendation['title'],
            ai_recommendation['contents']
        )
        
        logger.info(f"✅ 데모 추천 생성 및 하드웨어 전송 완료: {recommendation_id}")
        
        # 응답 반환
        return RecommendationCreateResponse(
            recommendation_id=recommendation_id,
            message="데모 추천이 하드웨어에 전송되었습니다"
        )
        
    except Exception as e:
        logger.error(f"❌ 데모 추천 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"데모 추천 생성 실패: {str(e)}")


@router.post("/feedback", response_model=RecommendationConfirmResponse)
async def feedback_recommendation(request: RecommendationConfirmRequest):
    """하드웨어팀에서 사용자 응답 피드백 처리"""
    try:
        # 추천 서비스 가져오기
        from app.core.database import get_database
        from app.services.recommendation_service import RecommendationService
        
        db = await get_database()
        recommendation_service = RecommendationService(db)
        
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