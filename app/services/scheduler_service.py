"""
GazeHome AI Services - Scheduler Service
스마트 홈 추천 스케줄러 서비스
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pytz

logger = logging.getLogger(__name__)

class SchedulerService:
    """스마트 홈 추천 스케줄러 서비스"""
    
    def __init__(self):
        self.is_running = False
        self.user_id = None
        self.interval_minutes = 30
        self.task = None
        self.last_check = None
        
    async def start(self, user_id: str, interval_minutes: int = 30):
        """스케줄러 시작"""
        if self.is_running:
            await self.stop()
        
        self.user_id = user_id
        self.interval_minutes = interval_minutes
        self.is_running = True
        
        # 백그라운드 태스크 시작
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info(f"스케줄러 시작: 사용자={user_id}, 간격={interval_minutes}분")
    
    async def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("스케줄러 중지")
    
    async def _run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.is_running:
            try:
                await self.run_once(self.user_id)
                await asyncio.sleep(self.interval_minutes * 60)  # 분을 초로 변환
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def run_once(self, user_id: str) -> Dict[str, Any]:
        """한 번만 추천 실행"""
        try:
            # 현재 시간 정보
            KST = pytz.timezone('Asia/Seoul')
            now = datetime.now(KST)
            self.last_check = now.isoformat()
            
            # 추천 조건 확인
            should_recommend = self._should_recommend(now)
            
            result = {
                "should_recommend": should_recommend,
                "timestamp": now.isoformat()
            }
            
            if should_recommend:
                # 실제 AI 추천 서비스 사용
                from app.api.endpoints.recommendations import AIRecommendationService
                
                ai_service = AIRecommendationService()
                context = f"자동 스케줄러 추천 (시간: {now.hour}시, 계절: {self._get_season(now.month)})"
                
                # AI 추천 생성
                recommendation = await ai_service.generate_smart_recommendation(context)
                
                result.update({
                    "title": recommendation.get("title", "스마트 홈 추천"),
                    "contents": recommendation.get("contents", "현재 상황에 맞는 기기 제어를 추천드립니다."),
                    "device_control": recommendation.get("device_control"),
                    "reason": f"자동 스케줄러 (시간: {now.hour}시, 계절: {self._get_season(now.month)})"
                })
                
                logger.info(f"✅ 스케줄러 AI 추천 생성: {result['title']}")
                
                # 제어 정보가 있으면 로그 출력
                if result.get("device_control"):
                    device_info = result["device_control"]
                    logger.info(f"🎯 제어 정보: {device_info.get('device_alias')} -> {device_info.get('action')}")
                
            else:
                result.update({
                    "reason": "추천 조건을 만족하지 않음"
                })
                logger.info("추천 조건 미충족")
            
            return result
            
        except Exception as e:
            logger.error(f"추천 실행 실패: {e}")
            return {
                "should_recommend": False,
                "timestamp": datetime.now(KST).isoformat(),
                "reason": f"오류 발생: {str(e)}"
            }
    
    def _should_recommend(self, now: datetime) -> bool:
        """추천 여부 판단"""
        # 간단한 추천 로직
        hour = now.hour
        
        # 모든 시간대에 추천 (테스트용)
        # 실제 운영에서는 특정 시간대로 제한 가능
        return True
        
        # 원래 로직 (주석 처리)
        # if hour in [7, 8, 12, 18, 19, 20, 21]:
        #     return True
        # if now.weekday() >= 5:  # 토요일, 일요일
        #     return hour in [9, 10, 14, 15, 16, 17, 22]
        # return False
    
    def _get_season(self, month: int) -> str:
        """월에 따른 계절 반환"""
        if month in [12, 1, 2]:
            return "겨울"
        elif month in [3, 4, 5]:
            return "봄"
        elif month in [6, 7, 8]:
            return "여름"
        else:
            return "가을"
    
    def get_status(self) -> Dict[str, Any]:
        """스케줄러 상태 반환"""
        return {
            "is_running": self.is_running,
            "user_id": self.user_id or "없음",
            "interval_minutes": self.interval_minutes,
            "last_check": self.last_check or "없음"
        }

# 전역 스케줄러 서비스 인스턴스
scheduler_service = SchedulerService()
