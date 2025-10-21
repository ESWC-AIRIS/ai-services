"""
GazeHome AI Services - LLM Service
LangChain과 Gemini API를 활용한 LLM 서비스
Memory 통합 Agent
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from app.mcp import mcp_client
from app.services.memory_service import get_memory_service

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM 서비스 클래스 (Memory-enabled Agent)
    
    Agent 구성:
    - Perception: 환경 인식 (기기 정보, 날씨, 시간)
    - Memory: 단기/장기 기억 (대화 히스토리, 사용자 선호도)
    - Reasoning: LLM 기반 추론
    - Action: 명령어 생성
    """
    
    def __init__(self, db_service=None):
        """LLM 서비스 초기화"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048,
            convert_system_message_to_human=True  # 시스템 메시지 변환
        )
        
        # Memory 통합
        self.memory = get_memory_service(db_service)
        
        logger.info(f"LLM 서비스 초기화 완료: {settings.GEMINI_MODEL}")
        logger.info(f"Gemini API 키 설정됨: {bool(settings.GEMINI_API_KEY)}")
        logger.info("Memory 통합 완료 (Short-term + Long-term)")
    
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
        MCP를 통해 날씨 정보를 활용하고, Memory를 통해 사용자 패턴을 반영합니다.
        
        Args:
            device_info: 클릭된 기기 정보 (device_id, device_type, current_state 등)
            context: 컨텍스트 정보 (user_id, session_id, 추가 정보 등)
        
        Returns:
            추천 정보 (prompt_text, action, reasoning)
        """
        try:
            user_id = context.get('user_id', 'unknown')
            session_id = context.get('session_id', 'unknown')
            
            # 1. Perception: 환경 정보 수집
            # MCP를 통해 날씨 정보 조회
            weather_info = await mcp_client.get_weather()
            weather_summary = await mcp_client.get_weather_summary()
            
            # 2. Memory: 사용자 기억 조회
            memory_context = await self.memory.get_full_context(user_id, session_id)
            short_term_summary = memory_context['short_term']['context_summary']
            long_term_insights = memory_context['long_term']['pattern_insights']
            
            # 3. Reasoning: LLM 프롬프트 구성
            system_prompt = """
            당신은 GazeHome의 Memory-enabled AI 추천 에이전트입니다.
            사용자가 시선으로 IoT 기기를 클릭했을 때, 그 의도를 심층적으로 분석하고 
            최적의 다음 명령어를 추천하는 역할을 합니다.
            
            고려사항:
            1. 기기의 현재 상태 (켜짐/꺼짐, 설정값 등)
            2. 현재 시간대 (아침/점심/저녁/밤)
            3. 기기 타입별 일반적인 사용 패턴
            4. 기기의 기능(capabilities)
            5. 사용자 편의성
            6. 현재 날씨 및 환경 조건 (온도, 습도, 날씨 상태)
            7. **최근 상호작용 히스토리 (Short-term Memory)**
            8. **사용자 선호도 및 패턴 (Long-term Memory)**
            
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
                "reasoning": "이렇게 추천한 이유 (날씨 정보 포함)"
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
            
            ## 날씨 정보 (MCP를 통해 조회)
            - 날씨 요약: {weather_summary}
            - 상세 정보: {weather_info}
            
            ## 🧠 Short-term Memory (최근 상호작용)
            {short_term_summary}
            
            ## 🎯 Long-term Memory (사용자 선호도 및 패턴)
            {long_term_insights}
            
            ## 추가 컨텍스트
            {context}
            
            위 정보를 바탕으로 사용자의 의도를 추론하고 최적의 명령어를 추천해주세요.
            **특히 Memory 정보(최근 상호작용 및 사용자 패턴)를 적극 활용하여 개인화된 추천을 제공하세요.**
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
                logger.info(f"기기 추천 생성 완료 (Memory + 날씨 정보 포함): {device_info.get('device_id')}")
                
                # 4. Action & Memory Update: 상호작용 기록
                interaction = {
                    'device_id': device_info.get('device_id'),
                    'device_name': device_info.get('device_name'),
                    'device_type': device_info.get('device_type'),
                    'action': result.get('action', {}).get('command'),
                    'intent': result.get('intent'),
                    'accepted': None  # 나중에 피드백으로 업데이트
                }
                self.memory.short_term.add_interaction(session_id, interaction)
                
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
                    "reasoning": f"{response.content} (날씨: {weather_summary})"
                }
                return result
            
        except Exception as e:
            logger.error(f"기기 추천 생성 실패: {e}")
            raise
    
    async def update_feedback(self, user_id: str, session_id: str, interaction_id: str, accepted: bool):
        """
        사용자 피드백 업데이트 (Long-term Memory 학습)
        
        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
            interaction_id: 상호작용 ID (device_id)
            accepted: 추천 수락 여부
        """
        # Short-term Memory에서 해당 상호작용 찾기
        history = self.memory.short_term.get_history(session_id)
        for interaction in history:
            if interaction.get('device_id') == interaction_id:
                interaction['accepted'] = accepted
                
                # Long-term Memory 학습
                await self.memory.long_term.learn_from_interaction(user_id, interaction)
                
                logger.info(f"피드백 업데이트 완료: {interaction_id}, accepted={accepted}")
                break
    
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