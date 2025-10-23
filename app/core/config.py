"""
GazeHome AI Services - Configuration
환경 설정 및 설정 관리
"""

from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# =============================================================================
# 애플리케이션 설정
# =============================================================================
APP_NAME = "GazeHome AI Services"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# =============================================================================
# 서버 설정
# =============================================================================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS 설정
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# =============================================================================
# MongoDB Atlas 설정
# =============================================================================
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "gazehome")

# =============================================================================
# AI API 설정
# =============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# =============================================================================
# 외부 API 엔드포인트
# =============================================================================
# Gateway 서버 (LG 기기 제어)
GATEWAY_ENDPOINT = os.getenv("GATEWAY_ENDPOINT", "http://localhost:9000/api/lg/control")

# 하드웨어 서버 (사용자 추천)
HARDWARE_ENDPOINT = os.getenv("HARDWARE_ENDPOINT", "http://localhost:8080/api/recommendations")

# =============================================================================
# Mock 서버 설정 (개발용)
# =============================================================================
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "9000"))
HARDWARE_PORT = int(os.getenv("HARDWARE_PORT", "8080"))
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
HARDWARE_HOST = os.getenv("HARDWARE_HOST", "0.0.0.0")

# =============================================================================
# 로깅 설정
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
