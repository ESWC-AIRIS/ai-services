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
        logger.info(f"Gemini API 키 설정됨: {bool(settings.GEMINI_API_KEY)}")
    
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
    
    async def generate_device_recommendation(
        self, 
        device_info: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        클릭된 IoT 기기에 대한 심층적 의도 추론 및 최적의 명령어 추천
        
        Args:
            device_info: 클릭된 기기 정보 (device_id, device_type, current_state 등)
            context: 컨텍스트 정보 (user_id, session_id, 추가 정보 등)
        
        Returns:
            추천 정보 (prompt_text, action, reasoning)
        """
        try:
            system_prompt = """
            당신은 GazeHome의 AI 추천 에이전트입니다.
            사용자가 시선으로 IoT 기기를 클릭했을 때, 그 의도를 심층적으로 분석하고 
            최적의 다음 명령어를 추천하는 역할을 합니다.
            
            고려사항:
            1. 기기의 현재 상태 (켜짐/꺼짐, 설정값 등)
            2. 현재 시간대 (아침/점심/저녁/밤)
            3. 기기 타입별 일반적인 사용 패턴
            4. 기기의 기능(capabilities)
            5. 사용자 편의성
            
            응답은 반드시 다음 JSON 형식으로 작성해주세요:
            {
                "intent": "추론된 사용자 의도",
                "confidence": 0.0-1.0,
                "prompt_text": "사용자에게 보여줄 추천 메시지 (한국어, 친근하게)",
                "action": {
                    "device_id": "기기 ID",
                    "command": "실행할 명령어",
                    "parameters": {추가 파라미터}
                },
                "reasoning": "이렇게 추천한 이유"
            }
            """
            
            # 현재 시간대 정보 추가
            from datetime import datetime
            import pytz
            KST = pytz.timezone('Asia/Seoul')
            current_time = datetime.now(KST)
            time_info = {
                "hour": current_time.hour,
                "time_period": self._get_time_period(current_time.hour),
                "weekday": current_time.strftime("%A")
            }
            
            human_prompt = f"""
            ## 클릭된 기기 정보
            - 기기 ID: {device_info.get('device_id')}
            - 기기 타입: {device_info.get('device_type')}
            - 기기 이름: {device_info.get('device_name')}
            - 표시 이름: {device_info.get('display_name')}
            - 기능: {device_info.get('capabilities', [])}
            - 현재 상태: {device_info.get('current_state', {})}
            
            ## 현재 시간 정보
            - 시간: {time_info['hour']}시
            - 시간대: {time_info['time_period']}
            - 요일: {time_info['weekday']}
            
            ## 추가 컨텍스트
            {context}
            
            위 정보를 바탕으로 사용자의 의도를 추론하고 최적의 명령어를 추천해주세요.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # JSON 파싱 시도
            import json
            import re
            
            # JSON 부분만 추출 (```json ... ``` 형태일 수 있음)
            content = response.content
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            elif '```' in content:
                # 일반 코드 블록
                json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            try:
                result = json.loads(content)
                logger.info(f"기기 추천 생성 완료: {device_info.get('device_id')}")
                return result
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조 반환
                logger.warning(f"LLM 응답 JSON 파싱 실패, 기본 구조 사용")
                result = {
                    "intent": "device_control",
                    "confidence": 0.7,
                    "prompt_text": f"{device_info.get('display_name', '기기')}를 제어하시겠습니까?",
                    "action": {
                        "device_id": device_info.get('device_id'),
                        "command": "toggle",
                        "parameters": {}
                    },
                    "reasoning": response.content
                }
                return result
            
        except Exception as e:
            logger.error(f"기기 추천 생성 실패: {e}")
            raise
    
    def _get_time_period(self, hour: int) -> str:
        """시간대 구분"""
        if 5 <= hour < 12:
            return "아침"
        elif 12 <= hour < 18:
            return "오후"
        elif 18 <= hour < 22:
            return "저녁"
        else:
            return "밤"