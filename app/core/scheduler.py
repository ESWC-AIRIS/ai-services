"""
GazeHome AI Services - Background Task Scheduler
APScheduler를 사용한 주기적 작업 스케줄러
"""

import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz

from app.services.proactive_recommendation_service import get_proactive_service
from app.services.hardware_client import get_hardware_client

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')


class RecommendationScheduler:
    """
    능동적 추천 스케줄러
    
    주기적으로 사용자들에게 추천을 생성하고 하드웨어로 전송합니다.
    """
    
    def __init__(self):
        """스케줄러 초기화"""
        self.scheduler = AsyncIOScheduler(timezone=KST)
        self.proactive_service = get_proactive_service()
        self.hardware_client = get_hardware_client()
        self.is_running = False
        logger.info("RecommendationScheduler 초기화 완료")
    
    def start(self, interval_minutes: int = 30):
        """
        스케줄러 시작
        
        Args:
            interval_minutes: 실행 주기 (분 단위, 기본 30분)
        """
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            return
        
        # 주기적 추천 작업 등록
        self.scheduler.add_job(
            self._run_proactive_recommendations,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='proactive_recommendation_job',
            name='능동적 추천 생성 및 전송',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(f"스케줄러 시작됨 (실행 주기: {interval_minutes}분)")
    
    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            logger.warning("스케줄러가 실행 중이 아닙니다")
            return
        
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("스케줄러 중지됨")
    
    async def _run_proactive_recommendations(self):
        """
        능동적 추천 실행 (모든 활성 사용자 대상)
        
        TODO: 실제로는 활성 사용자 목록을 DB에서 조회해야 함
        """
        try:
            logger.info("=== 능동적 추천 작업 시작 ===")
            start_time = datetime.now(KST)
            
            # TODO: MongoDB에서 활성 사용자 목록 조회
            # 현재는 테스트를 위해 예시 사용자 사용
            active_users = await self._get_active_users()
            
            logger.info(f"활성 사용자 수: {len(active_users)}")
            
            success_count = 0
            fail_count = 0
            
            for user_id in active_users:
                try:
                    # 사용자별 추천 생성
                    recommendation = await self.proactive_service.generate_proactive_recommendation(user_id)
                    
                    if recommendation and recommendation.get('should_recommend'):
                        # 하드웨어로 전송
                        sent = await self.hardware_client.send_recommendation(
                            user_id=user_id,
                            recommendation=recommendation
                        )
                        
                        if sent:
                            success_count += 1
                            logger.info(
                                f"✅ [{user_id}] 추천 전송 성공: "
                                f"\"{recommendation.get('prompt_text')}\" → {recommendation.get('device_id')}"
                            )
                        else:
                            fail_count += 1
                            logger.warning(
                                f"⚠️ [{user_id}] 추천 전송 실패: "
                                f"\"{recommendation.get('prompt_text')}\" → {recommendation.get('device_id')}"
                            )
                    else:
                        logger.info(f"추천 조건 미충족: user_id={user_id}")
                        
                except Exception as e:
                    fail_count += 1
                    logger.error(f"사용자 {user_id} 추천 처리 중 오류: {e}")
            
            end_time = datetime.now(KST)
            elapsed = (end_time - start_time).total_seconds()
            
            logger.info(
                f"=== 능동적 추천 작업 완료 === "
                f"성공: {success_count}, 실패: {fail_count}, "
                f"소요시간: {elapsed:.2f}초"
            )
            
        except Exception as e:
            logger.error(f"능동적 추천 작업 실패: {e}")
    
    async def _get_active_users(self) -> list:
        """
        활성 사용자 목록 조회
        
        TODO: 실제로는 MongoDB에서 조회
        - 최근 24시간 이내 활동한 사용자
        - 추천 수신을 허용한 사용자
        - 현재 온라인 상태인 사용자
        
        현재는 테스트용 예시 사용자 반환
        """
        # 예시 사용자 (나중에 DB 조회로 교체)
        return ["user_001", "user_002"]
    
    def get_status(self) -> dict:
        """스케줄러 상태 조회"""
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                })
        
        return {
            'is_running': self.is_running,
            'jobs': jobs,
            'timezone': str(KST)
        }


# 싱글톤 인스턴스
_scheduler: Optional[RecommendationScheduler] = None


def get_scheduler() -> RecommendationScheduler:
    """RecommendationScheduler 싱글톤 인스턴스 반환"""
    global _scheduler
    if _scheduler is None:
        _scheduler = RecommendationScheduler()
    return _scheduler

