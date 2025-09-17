"""
GazeHome AI Services - Main FastAPI Application
시선으로 제어하는 스마트 홈 AI 서버
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
import pytz

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.router import api_router


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
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info("GazeHome AI Services 시작 중...")
    await connect_to_mongo()
    logger.info("MongoDB 연결 완료")
    
    yield
    
    # 종료 시
    logger.info("GazeHome AI Services 종료 중...")
    await close_mongo_connection()
    logger.info("MongoDB 연결 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="GazeHome AI Services",
    description="시선으로 제어하는 스마트 홈 AI 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
