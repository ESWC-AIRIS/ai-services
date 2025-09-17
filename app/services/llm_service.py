"""
GazeHome AI Services - LLM Service
LangChain과 Gemini API를 활용한 LLM 서비스
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 서비스 클래스"""
    
    def __init__(self):
        """LLM 서비스 초기화"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048
        )
        logger.info(f"LLM 서비스 초기화 완료: {settings.GEMINI_MODEL}")
    
    async def analyze_intent(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 의도 분석"""
        try:
            system_prompt = """
            당신은 스마트 홈 제어를 위한 의도 분석 AI입니다.
            사용자의 시선 데이터와 맥락 정보를 바탕으로 의도를 분석해주세요.
            
            가능한 의도들:
            - device_control: 기기 제어
            - information_query: 정보 조회
            - automation_setup: 자동화 설정
            - preference_update: 선호도 업데이트
            
            응답 형식:
            {
                "intent": "의도",
                "confidence": 0.0-1.0,
                "entities": [추출된 엔티티들],
                "reasoning": "분석 근거"
            }
            """
            
            human_prompt = f"""
            사용자 입력: {user_input}
            맥락 정보: {context}
            
            위 정보를 바탕으로 사용자의 의도를 분석해주세요.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # 응답 파싱 (실제로는 JSON 파싱 로직 필요)
            result = {
                "intent": "device_control",
                "confidence": 0.85,
                "entities": [],
                "reasoning": response.content
            }
            
            logger.info(f"의도 분석 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"의도 분석 실패: {e}")
            raise
    
    async def generate_command(self, intent: str, entities: List[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """맞춤형 명령 생성"""
        try:
            system_prompt = """
            당신은 스마트 홈 기기 제어를 위한 명령 생성 AI입니다.
            사용자의 의도와 맥락을 바탕으로 적절한 기기 제어 명령을 생성해주세요.
            
            응답 형식:
            {
                "device_id": "기기ID",
                "action": "액션",
                "parameters": {파라미터들},
                "reasoning": "명령 생성 근거"
            }
            """
            
            human_prompt = f"""
            의도: {intent}
            엔티티: {entities}
            맥락: {context}
            
            위 정보를 바탕으로 기기 제어 명령을 생성해주세요.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # 응답 파싱 (실제로는 JSON 파싱 로직 필요)
            result = {
                "device_id": "light_001",
                "action": "toggle",
                "parameters": {"intensity": 80},
                "reasoning": response.content
            }
            
            logger.info(f"명령 생성 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"명령 생성 실패: {e}")
            raise
    
    async def analyze_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """맥락 분석"""
        try:
            system_prompt = """
            당신은 스마트 홈 맥락 분석 AI입니다.
            사용자의 상황, 환경, 선호도를 종합적으로 분석해주세요.
            
            분석 항목:
            - 시간대별 패턴
            - 환경 조건 (날씨, 온도 등)
            - 사용자 선호도
            - 기기 상태
            - 일정 정보
            """
            
            human_prompt = f"""
            맥락 데이터: {context_data}
            
            위 정보를 바탕으로 종합적인 맥락 분석을 수행해주세요.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            result = {
                "analysis": response.content,
                "recommendations": [],
                "patterns": {}
            }
            
            logger.info("맥락 분석 완료")
            return result
            
        except Exception as e:
            logger.error(f"맥락 분석 실패: {e}")
            raise
