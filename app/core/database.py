"""
GazeHome AI Services - Database Connection
MongoDB 연결 및 관리
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 전역 데이터베이스 인스턴스
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """MongoDB 연결"""
    global client, database
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.MONGODB_DATABASE]
        
        # 연결 테스트
        await client.admin.command('ping')
        logger.info(f"MongoDB 연결 성공: {settings.MONGODB_DATABASE}")
        
    except Exception as e:
        logger.warning(f"MongoDB 연결 실패: {e}")
        logger.warning("MongoDB 없이 서버를 시작합니다. 일부 기능이 제한될 수 있습니다.")
        client = None
        database = None


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    global client
    
    if client:
        client.close()
        logger.info("MongoDB 연결 종료")


def get_database() -> AsyncIOMotorDatabase:
    """데이터베이스 인스턴스 반환"""
    return database
