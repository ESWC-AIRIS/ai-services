"""
GazeHome AI Services - Proactive Recommendation Service
주기적으로 사용자에게 능동적인 추천을 제공하는 서비스
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pytz
from app.services.llm_service import LLMService
from app.services.mongodb_service import MongoDBService
from app.mcp import mcp_client

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')


class ProactiveRecommendationService:
    """
    주기적 추천 서비스
    
    기능:
    1. 주기적으로 실행 (기본: 30분마다)
    2. 현재 컨텍스트 분석 (시간, 날씨, 사용자 패턴)
    3. 추천할 기기와 명령어 결정
    4. 하드웨어에 추천 전송
    """
    
    def __init__(self, llm_service: LLMService = None, db_service: MongoDBService = None):
        """서비스 초기화"""
        self.llm_service = llm_service or LLMService()
        self.db_service = db_service or MongoDBService()
        logger.info("ProactiveRecommendationService 초기화 완료")
    
    async def generate_proactive_recommendation(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 사용자에 대한 능동적 추천 생성
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            추천 정보 또는 None (추천할 것이 없는 경우)
        """
        try:
            logger.info(f"능동적 추천 생성 시작: user_id={user_id}")
            
            # 1. 현재 컨텍스트 수집
            context = await self._collect_context(user_id)
            
            # 2. 추천 가능한 기기 목록 조회
            available_devices = await self._get_available_devices(user_id)
            
            if not available_devices:
                logger.info(f"사용자 {user_id}의 사용 가능한 기기 없음")
                return None
            
            # 3. LLM을 통한 추천 생성
            recommendation = await self._generate_recommendation_with_llm(
                user_id=user_id,
                context=context,
                available_devices=available_devices
            )
            
            # 4. 추천 저장 (MongoDB)
            if recommendation and recommendation.get('should_recommend'):
                await self._save_recommendation(user_id, recommendation)
                logger.info(f"능동적 추천 생성 완료: {recommendation.get('device_id')}")
                return recommendation
            else:
                logger.info(f"추천 조건 미충족: user_id={user_id}")
                return None
                
        except Exception as e:
            logger.error(f"능동적 추천 생성 실패: user_id={user_id}, error={e}")
            return None
    
    async def _collect_context(self, user_id: str) -> Dict[str, Any]:
        """현재 컨텍스트 수집"""
        current_time = datetime.now(KST)
        
        # 날씨 정보 조회 (MCP)
        try:
            weather_info = await mcp_client.get_weather()
            weather_summary = await mcp_client.get_weather_summary()
        except Exception as e:
            logger.warning(f"날씨 정보 조회 실패: {e}")
            weather_info = {}
            weather_summary = "날씨 정보 없음"
        
        # 사용자 메모리 컨텍스트 조회
        try:
            memory_context = await self.llm_service.memory.get_full_context(
                user_id=user_id,
                session_id=f"proactive_{current_time.strftime('%Y%m%d')}"
            )
        except Exception as e:
            logger.warning(f"메모리 컨텍스트 조회 실패: {e}")
            memory_context = {
                'short_term': {'context_summary': '이력 없음'},
                'long_term': {'pattern_insights': '패턴 없음'}
            }
        
        context = {
            "timestamp": current_time.isoformat(),
            "time_info": {
                "hour": current_time.hour,
                "time_period": self._get_time_period(current_time.hour),
                "weekday": current_time.strftime("%A"),
                "date": current_time.strftime("%Y-%m-%d")
            },
            "weather": {
                "summary": weather_summary,
                "details": weather_info
            },
            "memory": memory_context
        }
        
        return context
    
    async def _get_available_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """
        사용자의 사용 가능한 기기 목록 조회
        
        TODO: 실제로는 MongoDB에서 사용자의 기기 목록을 조회해야 함
        현재는 예시 데이터 반환 (에어컨 & 공기청정기만)
        """
        # 예시 기기 목록 (에어컨 & 공기청정기만)
        example_devices = [
            {
                "device_id": "ac_living_room",
                "device_type": "air_conditioner",
                "device_name": "거실 에어컨",
                "display_name": "에어컨",
                "capabilities": ["on_off", "temperature", "mode"],
                "current_state": {"is_on": False, "temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "ac_bedroom",
                "device_type": "air_conditioner",
                "device_name": "침실 에어컨",
                "display_name": "에어컨",
                "capabilities": ["on_off", "temperature", "mode"],
                "current_state": {"is_on": False, "temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "air_purifier_living_room",
                "device_type": "air_purifier",
                "device_name": "거실 공기청정기",
                "display_name": "공기청정기",
                "capabilities": ["on_off", "fan_speed", "mode"],
                "current_state": {"is_on": False, "fan_speed": 1, "mode": "auto"}
            },
            {
                "device_id": "air_purifier_bedroom",
                "device_type": "air_purifier",
                "device_name": "침실 공기청정기",
                "display_name": "공기청정기",
                "capabilities": ["on_off", "fan_speed", "mode"],
                "current_state": {"is_on": False, "fan_speed": 1, "mode": "sleep"}
            }
        ]
        
        return example_devices
    
    async def _generate_recommendation_with_llm(
        self,
        user_id: str,
        context: Dict[str, Any],
        available_devices: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """LLM을 통한 추천 생성"""
        from langchain.schema import SystemMessage, HumanMessage
        
        system_prompt = """
당신은 GazeHome의 능동적(Proactive) AI 추천 에이전트입니다.
사용자가 요청하지 않아도, 현재 상황을 분석하여 적절한 타이밍에 
유용한 기기 제어를 추천하는 역할을 합니다.

## 중요 원칙
1. **필요할 때만 추천**: 명확한 이유가 있을 때만 추천
2. **하나의 추천**: 한 번에 하나의 기기만 추천
3. **개인화**: 사용자의 과거 패턴과 선호도 고려
4. **상황 적합성**: 시간, 날씨, 환경 조건 고려

## 추천하면 좋은 상황 예시
- 아침에 일어날 시간 → 조명 켜기
- 더운 날씨 + 에어컨 꺼짐 → 에어컨 켜기
- 미세먼지 나쁨 + 공기청정기 꺼짐 → 공기청정기 켜기
- 저녁 시간 + 조명 꺼짐 → 조명 켜기
- 사용자가 평소 이 시간에 특정 기기를 사용 → 해당 기기 제어

## 추천하지 말아야 할 상황
- 이미 기기가 적절하게 작동 중
- 특별한 이유가 없음
- 사용자 패턴과 맞지 않음
- 너무 자주 추천

응답은 반드시 다음 JSON 형식으로 작성:
{
    "should_recommend": true/false,
    "device_id": "추천할 기기 ID (should_recommend가 true일 때)",
    "device_name": "기기 이름",
    "confidence": 0.0-1.0,
    "prompt_text": "사용자에게 보여줄 추천 메시지 (친근하고 짧게)",
    "action": {
        "command": "실행할 명령어",
        "parameters": {}
    },
            "reasoning": "왜 이 추천을 하는지 이유"
        }
"""
        
        # Memory 정보 추출 (없으면 기본값 사용 - 데모 모드 대응)
        memory = context.get('memory', {})
        short_term_summary = memory.get('short_term', {}).get('context_summary', '이력 없음')
        long_term_insights = memory.get('long_term', {}).get('pattern_insights', '패턴 없음')
        
        human_prompt = f"""
## 현재 시간 정보
- 시간: {context['time_info']['hour']}시
- 시간대: {context['time_info']['time_period']}
- 요일: {context['time_info']['weekday']}

## 날씨 정보
- 요약: {context['weather']['summary']}
- 상세: {context['weather']['details']}

## 사용자 메모리
- 최근 상호작용: {short_term_summary}
- 사용자 패턴: {long_term_insights}

## 사용 가능한 기기 목록
{self._format_devices(available_devices)}

위 정보를 바탕으로 **지금 이 순간** 사용자에게 추천할 만한 기기 제어가 있는지 판단하고,
있다면 **하나의 기기**만 추천해주세요.

명확한 이유가 없다면 should_recommend를 false로 설정하세요.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await self.llm_service.llm.ainvoke(messages)
            
            # JSON 파싱
            import json
            import re
            
            content = response.content
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            elif '```' in content:
                json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            result = json.loads(content)
            
            # 추천 내용을 로그에 상세히 출력
            if result.get('should_recommend'):
                logger.info(f"📢 추천 생성됨:")
                logger.info(f"  - 기기: {result.get('device_name')} ({result.get('device_id')})")
                logger.info(f"  - 추천 문구: \"{result.get('prompt_text')}\"")
                logger.info(f"  - 명령어: {result.get('action', {}).get('command')}")
                logger.info(f"  - 이유: {result.get('reasoning')}")
                logger.info(f"  - 신뢰도: {result.get('confidence')}")
            else:
                logger.info(f"추천 조건 미충족 (should_recommend=false)")
            
            return result
            
        except Exception as e:
            logger.error(f"LLM 추천 생성 실패: {e}")
            return None
    
    def _format_devices(self, devices: List[Dict[str, Any]]) -> str:
        """기기 목록을 읽기 쉬운 형태로 포맷"""
        formatted = []
        for device in devices:
            formatted.append(f"""
- {device['device_name']} ({device['device_type']})
  ID: {device['device_id']}
  기능: {', '.join(device['capabilities'])}
  현재 상태: {device['current_state']}
""")
        return '\n'.join(formatted)
    
    async def _save_recommendation(self, user_id: str, recommendation: Dict[str, Any]):
        """추천 정보를 MongoDB에 저장"""
        try:
            record = {
                "user_id": user_id,
                "recommendation": recommendation,
                "timestamp": datetime.now(KST),
                "status": "pending",  # pending, accepted, rejected
                "recommendation_type": "proactive_periodic"
            }
            
            await self.db_service.insert_one("proactive_recommendations", record)
            logger.info(f"추천 저장 완료: user_id={user_id}")
            
        except Exception as e:
            logger.warning(f"추천 저장 실패: {e}")
    
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


# 싱글톤 인스턴스
_proactive_service: Optional[ProactiveRecommendationService] = None


def get_proactive_service(
    llm_service: LLMService = None,
    db_service: MongoDBService = None
) -> ProactiveRecommendationService:
    """ProactiveRecommendationService 싱글톤 인스턴스 반환"""
    global _proactive_service
    if _proactive_service is None:
        _proactive_service = ProactiveRecommendationService(llm_service, db_service)
    return _proactive_service

