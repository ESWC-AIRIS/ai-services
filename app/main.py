"""
GazeHome AI Services - Main FastAPI Application
시선으로 제어하는 스마트 홈 AI 서버 (명세서에 맞춤)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
import pytz
from app.core.config import *
from app.api.router import api_router
from app.services.device_service import device_service

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [KST] %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리 (MCP 도구 포함)"""
    # 시작 시
    logger.info("GazeHome AI Services 시작 중...")
    logger.info(f"서버 설정: {HOST}:{PORT}")
    logger.info(f"Gateway URL: {GATEWAY_URL}")
    logger.info(f"Hardware URL: {HARDWARE_URL}")
    logger.info(f"Gateway Control: {GATEWAY_CONTROL_ENDPOINT}")
    logger.info(f"Hardware Recommendations: {HARDWARE_RECOMMENDATIONS_ENDPOINT}")
    logger.info(f"MongoDB 데이터베이스: {MONGODB_DATABASE}")
    
    # MongoDB 연결
    try:
        await device_service.connect()
        logger.info("MongoDB 연결 완료")
    except Exception as e:
        logger.warning(f"MongoDB 연결 실패: {e}")
    
    # 추천 Agent 초기화 확인
    try:
        from app.agents.recommendation_agent import create_agent
        agent = create_agent()
        if agent and agent.agent_executor:
            logger.info("추천 Agent 초기화 완료")
            
            # Agent에 도구가 제대로 등록되었는지 확인
            if hasattr(agent.agent_executor, 'tools'):
                logger.info(f"Agent 도구 개수: {len(agent.agent_executor.tools)}")
                for i, tool in enumerate(agent.agent_executor.tools):
                    logger.info(f"  - 도구 {i+1}: {tool.name}")
        else:
            logger.info("추천 Agent 초기화 실패")
    except Exception as e:
        logger.warning(f"추천 Agent 초기화 확인 실패: {e}")
    
    # 스케줄러 자동 시작 (환경변수로 제어)
    if SCHEDULER_AUTO_START:
        try:
            from app.services.scheduler_service import scheduler_service
            await scheduler_service.start(
                user_id=SCHEDULER_USER_ID,
                interval_minutes=SCHEDULER_INTERVAL_MINUTES
            )
            logger.info(f"스케줄러 자동 시작 완료 (간격: {SCHEDULER_INTERVAL_MINUTES}분)")
        except Exception as e:
            logger.warning(f"스케줄러 자동 시작 실패: {e}")
    
    yield
    
    # 종료 시
    logger.info("GazeHome AI Services 종료 중...")
    
    # 추천 Agent 정리
    try:
        from app.agents.recommendation_agent import recommendation_agent
        if recommendation_agent:
            await recommendation_agent.close()
            logger.info("추천 Agent 정리 완료")
    except Exception as e:
        logger.warning(f"추천 Agent 정리 실패: {e}")
    
    # MongoDB 연결 해제
    await device_service.disconnect()


# 기본 FastAPI 앱 생성
base_app = FastAPI(
    title="GazeHome AI Services",
    description="시선으로 제어하는 스마트 홈 AI 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 추천 Agent 통합
from app.agents.recommendation_agent import create_agent
recommendation_agent = create_agent()

# 기본 FastAPI 앱 사용
app = base_app

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "GazeHome AI Services",
        "description": "시선으로 제어하는 스마트 홈 AI 서버",
        "version": "1.0.0",
        "timestamp": datetime.now(KST).isoformat()
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(KST).isoformat(),
        "service": "GazeHome AI Services"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,  # MCP 연결 안정성을 위해 reload 비활성화
        log_level="info"
    )