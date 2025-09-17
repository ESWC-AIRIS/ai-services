"""
GazeHome AI Services - Logger Utility
로깅 유틸리티
"""

import logging
import sys
from datetime import datetime
import pytz
from app.core.config import settings

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')


class KSTFormatter(logging.Formatter):
    """한국 시간대 포맷터"""
    
    def formatTime(self, record, datefmt=None):
        """시간을 한국 시간대로 포맷"""
        ct = datetime.fromtimestamp(record.created, tz=KST)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.strftime('%Y-%m-%d %H:%M:%S')
        return s


def setup_logger(name: str = "gazehome") -> logging.Logger:
    """로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 포맷터 설정
    formatter = KSTFormatter(
        fmt='%(asctime)s [KST] %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


# 전역 로거 인스턴스
logger = setup_logger()
