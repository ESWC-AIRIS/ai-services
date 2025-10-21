"""
GazeHome AI Services - Memory Service
Agent의 Short-term 및 Long-term Memory 관리
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    단기 기억 (Short-term Memory)
    - 현재 세션의 대화 히스토리
    - 최근 N개의 상호작용 저장
    - 컨텍스트 윈도우 관리
    """
    
    def __init__(self, max_size: int = 10):
        """
        Args:
            max_size: 저장할 최대 상호작용 수
        """
        self.max_size = max_size
        self.sessions: Dict[str, deque] = {}
        logger.info(f"Short-term Memory 초기화 (max_size={max_size})")
    
    def add_interaction(self, session_id: str, interaction: Dict[str, Any]):
        """상호작용 추가"""
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_size)
        
        interaction['timestamp'] = datetime.now().isoformat()
        self.sessions[session_id].append(interaction)
        
        logger.debug(f"세션 {session_id}에 상호작용 추가: {len(self.sessions[session_id])}개")
    
    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """세션의 히스토리 조회"""
        if session_id not in self.sessions:
            return []
        
        history = list(self.sessions[session_id])
        if last_n:
            history = history[-last_n:]
        
        return history
    
    def get_context_summary(self, session_id: str) -> str:
        """세션의 컨텍스트 요약"""
        history = self.get_history(session_id)
        
        if not history:
            return "이전 상호작용 없음"
        
        # 최근 상호작용 요약
        recent = history[-3:]  # 최근 3개
        summary_parts = []
        
        for interaction in recent:
            device = interaction.get('device_name', '기기')
            action = interaction.get('action', '제어')
            summary_parts.append(f"- {device}: {action}")
        
        return "\n".join(summary_parts)
    
    def clear_session(self, session_id: str):
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"세션 {session_id} 삭제됨")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """오래된 세션 정리"""
        now = datetime.now()
        sessions_to_remove = []
        
        for session_id, interactions in self.sessions.items():
            if not interactions:
                sessions_to_remove.append(session_id)
                continue
            
            # 마지막 상호작용 시간 확인
            last_interaction = interactions[-1]
            last_time = datetime.fromisoformat(last_interaction['timestamp'])
            
            if (now - last_time).total_seconds() > max_age_hours * 3600:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.clear_session(session_id)
        
        if sessions_to_remove:
            logger.info(f"{len(sessions_to_remove)}개의 오래된 세션 정리됨")


class LongTermMemory:
    """
    장기 기억 (Long-term Memory)
    - 사용자 선호도
    - 패턴 학습
    - MongoDB/Vector DB 연동
    """
    
    def __init__(self, db_service=None):
        """
        Args:
            db_service: MongoDB 서비스 인스턴스
        """
        self.db_service = db_service
        self.user_preferences: Dict[str, Dict] = {}
        logger.info("Long-term Memory 초기화")
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """사용자 선호도 조회"""
        # 캐시 확인
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # DB에서 조회
        if self.db_service:
            try:
                prefs = await self.db_service.find_one(
                    "user_preferences",
                    {"user_id": user_id}
                )
                if prefs:
                    self.user_preferences[user_id] = prefs
                    return prefs
            except Exception as e:
                logger.error(f"사용자 선호도 조회 실패: {e}")
        
        # 기본값 반환
        return {
            "user_id": user_id,
            "temperature_preference": 24,
            "brightness_preference": 70,
            "favorite_devices": [],
            "time_patterns": {}
        }
    
    async def update_user_preference(self, user_id: str, preference_data: Dict[str, Any]):
        """사용자 선호도 업데이트"""
        if self.db_service:
            try:
                await self.db_service.update_one(
                    "user_preferences",
                    {"user_id": user_id},
                    {"$set": preference_data},
                    upsert=True
                )
                # 캐시 업데이트
                if user_id in self.user_preferences:
                    self.user_preferences[user_id].update(preference_data)
                
                logger.info(f"사용자 {user_id} 선호도 업데이트됨")
            except Exception as e:
                logger.error(f"사용자 선호도 업데이트 실패: {e}")
    
    async def learn_from_interaction(self, user_id: str, interaction: Dict[str, Any]):
        """상호작용에서 학습"""
        # 사용자가 수락한 추천에서 패턴 학습
        if interaction.get('accepted'):
            device_type = interaction.get('device_type')
            time_of_day = interaction.get('time_of_day')
            parameters = interaction.get('parameters', {})
            
            # 시간대별 패턴 업데이트
            prefs = await self.get_user_preferences(user_id)
            time_patterns = prefs.get('time_patterns', {})
            
            if time_of_day not in time_patterns:
                time_patterns[time_of_day] = {}
            
            if device_type not in time_patterns[time_of_day]:
                time_patterns[time_of_day][device_type] = []
            
            time_patterns[time_of_day][device_type].append(parameters)
            
            await self.update_user_preference(user_id, {
                'time_patterns': time_patterns
            })
            
            logger.info(f"사용자 {user_id}의 패턴 학습 완료")
    
    async def get_pattern_insights(self, user_id: str, context: Dict[str, Any]) -> str:
        """패턴 기반 인사이트 생성"""
        prefs = await self.get_user_preferences(user_id)
        time_of_day = context.get('time_of_day', 'unknown')
        
        insights = []
        
        # 시간대별 패턴
        time_patterns = prefs.get('time_patterns', {})
        if time_of_day in time_patterns:
            insights.append(f"이 시간대에 자주 사용하는 기기: {', '.join(time_patterns[time_of_day].keys())}")
        
        # 선호 온도
        temp_pref = prefs.get('temperature_preference')
        if temp_pref:
            insights.append(f"선호 온도: {temp_pref}℃")
        
        # 선호 밝기
        brightness_pref = prefs.get('brightness_preference')
        if brightness_pref:
            insights.append(f"선호 밝기: {brightness_pref}%")
        
        return "\n".join(insights) if insights else "학습된 패턴 없음"


class MemoryService:
    """
    통합 Memory 서비스
    Short-term + Long-term Memory 관리
    """
    
    def __init__(self, db_service=None):
        self.short_term = ShortTermMemory(max_size=10)
        self.long_term = LongTermMemory(db_service)
        logger.info("Memory Service 초기화 완료")
    
    async def get_full_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """전체 컨텍스트 조회 (단기 + 장기 기억)"""
        # Short-term: 세션 히스토리
        recent_history = self.short_term.get_history(session_id, last_n=5)
        context_summary = self.short_term.get_context_summary(session_id)
        
        # Long-term: 사용자 선호도 및 패턴
        user_prefs = await self.long_term.get_user_preferences(user_id)
        pattern_insights = await self.long_term.get_pattern_insights(user_id, {})
        
        return {
            "short_term": {
                "recent_history": recent_history,
                "context_summary": context_summary
            },
            "long_term": {
                "user_preferences": user_prefs,
                "pattern_insights": pattern_insights
            }
        }
    
    async def add_and_learn(self, user_id: str, session_id: str, interaction: Dict[str, Any]):
        """상호작용 추가 및 학습"""
        # Short-term에 추가
        self.short_term.add_interaction(session_id, interaction)
        
        # Long-term 학습
        await self.long_term.learn_from_interaction(user_id, interaction)


# Singleton 인스턴스
_memory_service: Optional[MemoryService] = None


def get_memory_service(db_service=None) -> MemoryService:
    """Memory Service 싱글톤 인스턴스 반환"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService(db_service)
    return _memory_service

