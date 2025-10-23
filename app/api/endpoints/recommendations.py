"""
GazeHome AI Services - Recommendations Endpoints
AI → HW 추천 시스템 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging
import httpx
import google.generativeai as genai
from app.core.config import *

router = APIRouter()
logger = logging.getLogger(__name__)


class RecommendationRequest(BaseModel):
    """AI → HW 추천 요청 (명세서)"""
    title: str = Field(..., description="추천 제목 (예: 에어컨 킬까요?)")
    contents: str = Field(..., description="추천 내용")


class RecommendationResponse(BaseModel):
    """AI → HW 추천 응답 (명세서)"""
    message: str
    confirm: str = Field(..., description="사용자 확인 (YES/NO)")


class HardwareClient:
    """하드웨어 통신 클라이언트"""
    
    def __init__(self, hardware_endpoint: str = HARDWARE_ENDPOINT):
        self.hardware_endpoint = hardware_endpoint
        self.timeout = 10.0
        logger.info(f"HardwareClient 초기화: endpoint={self.hardware_endpoint}")
    
    async def send_recommendation(self, title: str, contents: str) -> Dict[str, Any]:
        """하드웨어로 추천 전송"""
        try:
            payload = {
                "title": title,
                "contents": contents
            }
            
            logger.info(f"🚀 하드웨어로 추천 전송:")
            logger.info(f"  - 제목: \"{title}\"")
            logger.info(f"  - 내용: \"{contents}\"")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.hardware_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    confirm = result.get('confirm', 'NO')
                    logger.info(f"✅ 하드웨어 응답 수신: {confirm}")
                    return result
                else:
                    logger.error(f"❌ 하드웨어 통신 실패: status={response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"하드웨어 통신 실패: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"하드웨어 통신 타임아웃: title={title}")
            raise HTTPException(status_code=504, detail="하드웨어 통신 타임아웃")
        except httpx.RequestError as e:
            logger.error(f"하드웨어 통신 에러: {e}")
            raise HTTPException(status_code=503, detail=f"하드웨어 통신 에러: {str(e)}")
        except Exception as e:
            logger.error(f"추천 전송 중 예외 발생: {e}")
            raise HTTPException(status_code=500, detail=f"추천 전송 실패: {str(e)}")


# Gemini AI 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# 하드웨어 클라이언트 인스턴스
hardware_client = HardwareClient()

class AIRecommendationService:
    """AI 추천 서비스"""
    
    def __init__(self):
        self.model = model
    
    async def generate_smart_recommendation(self, context: str = None) -> Dict[str, str]:
        """AI가 스마트 추천 생성"""
        if not self.model:
            # Gemini API가 없으면 기본 추천 반환
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."
            }
        
        try:
            prompt = f"""
            당신은 스마트 홈 AI 어시스턴트입니다. 
            사용자의 현재 상황을 분석하여 적절한 기기 제어 추천을 해주세요.
            
            상황: {context or "일반적인 스마트 홈 환경"}
            
            다음 형식으로 응답해주세요:
            제목: [추천 제목]
            내용: [추천 내용]
            
            예시:
            제목: 에어컨 킬까요?
            내용: 현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다.
            """
            
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # 응답 파싱
            lines = result.split('\n')
            title = "스마트 홈 추천"
            contents = "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."
            
            for line in lines:
                if line.startswith('제목:'):
                    title = line.replace('제목:', '').strip()
                elif line.startswith('내용:'):
                    contents = line.replace('내용:', '').strip()
            
            return {
                "title": title,
                "contents": contents
            }
            
        except Exception as e:
            logger.error(f"AI 추천 생성 실패: {e}")
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."
            }

# AI 추천 서비스 인스턴스
ai_service = AIRecommendationService()


@router.post("/", response_model=RecommendationResponse)
async def send_smart_recommendation(request: RecommendationRequest):
    """
    AI → HW: 추천 문구 전달 (유저 컨펌용) (명세서)
    
    AI가 유저별 맞춤형 추천을 생성하여 하드웨어(유저)에게 허가를 요청합니다.
    """
    try:
        logger.info(f"🤖 AI → HW 추천 전송:")
        logger.info(f"  - 제목: \"{request.title}\"")
        logger.info(f"  - 내용: \"{request.contents}\"")
        
        # 하드웨어로 추천 전송
        hardware_response = await hardware_client.send_recommendation(
            title=request.title,
            contents=request.contents
        )
        
        # 응답 검증
        confirm = hardware_response.get('confirm', 'NO')
        if confirm not in ['YES', 'NO']:
            confirm = 'NO'  # 기본값
        
        return RecommendationResponse(
            message="추천 문구 유저 피드백",
            confirm=confirm
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"추천 전송 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"추천 전송 실패: {str(e)}"
        )



