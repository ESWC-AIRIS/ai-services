"""
GazeHome AI Services - Database Configuration
MongoDB 연결 및 데이터베이스 관리
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import MONGODB_URL, MONGODB_DATABASE

logger = logging.getLogger(__name__)

# 전역 데이터베이스 클라이언트
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def get_database() -> AsyncIOMotorDatabase:
    """MongoDB 데이터베이스 인스턴스 반환"""
    global _database
    
    if _database is None:
        await connect_to_mongo()
    
    return _database


async def connect_to_mongo():
    """MongoDB에 연결"""
    global _client, _database
    
    try:
        _client = AsyncIOMotorClient(MONGODB_URL)
        _database = _client[MONGODB_DATABASE]
        
        # 연결 테스트
        await _client.admin.command('ping')
        logger.info("✅ MongoDB 연결 성공")
        
    except Exception as e:
        logger.error(f"❌ MongoDB 연결 실패: {e}")
        raise


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    global _client
    
    if _client:
        _client.close()
        logger.info("✅ MongoDB 연결 종료")
