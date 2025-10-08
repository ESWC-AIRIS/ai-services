"""
GazeHome AI Services - Configuration
환경 설정 및 설정 관리
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    APP_NAME: str = "GazeHome AI Services"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 설정
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # MongoDB 설정
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "gazehome"
    
    # Gemini API 설정
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"  # 기본 모델로 변경
    
    # Vector DB 설정 (ChromaDB)
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # LangSmith/LangFuse 설정
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "gazehome-ai"
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # 외부 API 설정
    WEATHER_API_KEY: Optional[str] = None
    CALENDAR_API_KEY: Optional[str] = None
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()
