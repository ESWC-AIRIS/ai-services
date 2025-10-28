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
# Weather MCP 설정
# =============================================================================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_WEATHER_SCENARIO = os.getenv("DEMO_WEATHER_SCENARIO", "summer_heat")

# =============================================================================
# 외부 API 엔드포인트
# =============================================================================
# Gateway 서버 기본 URL
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:9000")

# 하드웨어 서버 기본 URL  
HARDWARE_URL = os.getenv("HARDWARE_URL", "http://localhost:8080")

# API 엔드포인트 경로
GATEWAY_CONTROL_ENDPOINT = f"{GATEWAY_URL}/api/lg/control"
GATEWAY_DEVICES_ENDPOINT = f"{GATEWAY_URL}/api/lg/devices"
HARDWARE_RECOMMENDATIONS_ENDPOINT = f"{HARDWARE_URL}/api/recommendations/"

# =============================================================================
# Mock 서버 설정 (개발용 - examples/mock_servers.py에서만 사용)
# =============================================================================
MOCK_GATEWAY_PORT = int(os.getenv("MOCK_GATEWAY_PORT", "9000"))
MOCK_HARDWARE_PORT = int(os.getenv("MOCK_HARDWARE_PORT", "8080"))
MOCK_GATEWAY_HOST = os.getenv("MOCK_GATEWAY_HOST", "0.0.0.0")
MOCK_HARDWARE_HOST = os.getenv("MOCK_HARDWARE_HOST", "0.0.0.0")

# =============================================================================
# 스케줄러 설정
# =============================================================================
SCHEDULER_AUTO_START = os.getenv("SCHEDULER_AUTO_START", "false").lower() == "true"
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "30"))
SCHEDULER_USER_ID = os.getenv("SCHEDULER_USER_ID", "default_user")

# =============================================================================
# 로깅 설정
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

