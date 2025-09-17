"""
GazeHome AI Services - Main Entry Point
시선으로 제어하는 스마트 홈 AI 서버 메인 진입점
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
