"""
GazeHome AI Services - Configuration
환경 설정 및 설정 관리
"""

from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경변수에서 설정값 가져오기 (하드코딩 제거)
APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 서버 설정
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", "8000"))

# CORS 설정
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# MongoDB 설정
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# Vector DB 설정 (ChromaDB)
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH")

# LangSmith/LangFuse 설정
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

# 외부 API 설정
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CALENDAR_API_KEY = os.getenv("CALENDAR_API_KEY")

# 하드웨어 통신 설정
HARDWARE_ENDPOINT = os.getenv("HARDWARE_ENDPOINT")

# IoT 기기 제어 API 설정
IOT_API_ENDPOINT = os.getenv("IOT_API_ENDPOINT")

# Gateway 통신 설정
GATEWAY_ENDPOINT = os.getenv("GATEWAY_ENDPOINT")

# 능동적 추천 설정
PROACTIVE_RECOMMENDATION_ENABLED = os.getenv("PROACTIVE_RECOMMENDATION_ENABLED", "true").lower() == "true"
PROACTIVE_RECOMMENDATION_INTERVAL_MINUTES = int(os.getenv("PROACTIVE_RECOMMENDATION_INTERVAL_MINUTES", "30"))

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
