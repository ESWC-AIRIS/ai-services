"""
GazeHome AI Services - Weather MCP Server
날씨 정보를 제공하는 MCP 서버
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherMCPServer:
    """날씨 정보 MCP 서버"""
    
    def __init__(self):
        """Weather MCP 서버 초기화"""
        self.api_key = getattr(settings, 'WEATHER_API_KEY', None)
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.default_location = "Seoul,KR"  # 기본 위치: 서울
        
        if not self.api_key:
            logger.warning("WEATHER_API_KEY가 설정되지 않았습니다. 모의 데이터를 사용합니다.")
        
        logger.info("Weather MCP Server 초기화 완료")
    
    async def get_current_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        현재 날씨 정보 조회
        
        Args:
            location: 위치 (예: "Seoul,KR", "New York,US")
        
        Returns:
            날씨 정보 딕셔너리
        """
        try:
            if not self.api_key:
                # API 키가 없으면 모의 데이터 반환
                return self._get_mock_weather_data()
            
            location = location or self.default_location
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",  # 섭씨 온도
                    "lang": "kr"  # 한국어 응답
                }
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답 데이터 정리
                weather_info = {
                    "location": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"],
                    "main": data["weather"][0]["main"],
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "visibility": data.get("visibility", 0) / 1000,  # km로 변환
                    "timestamp": datetime.now().isoformat(),
                    "source": "openweathermap"
                }
                
                logger.info(f"날씨 정보 조회 완료: {location} - {weather_info['temperature']}℃")
                return weather_info
                
        except httpx.TimeoutException:
            logger.error(f"날씨 API 타임아웃: {location}")
            return self._get_mock_weather_data()
        except httpx.HTTPStatusError as e:
            logger.error(f"날씨 API HTTP 오류: {e.response.status_code}")
            return self._get_mock_weather_data()
        except Exception as e:
            logger.error(f"날씨 정보 조회 실패: {e}")
            return self._get_mock_weather_data()
    
    async def get_weather_alerts(self, location: Optional[str] = None) -> list:
        """
        날씨 경보 정보 조회 (OpenWeatherMap One Call API 필요)
        
        Args:
            location: 위치
        
        Returns:
            경보 정보 리스트
        """
        try:
            # One Call API는 유료이므로 간단한 경보 로직 구현
            weather = await self.get_current_weather(location)
            alerts = []
            
            # 간단한 경보 조건
            if weather["temperature"] > 35:
                alerts.append({
                    "type": "heat_warning",
                    "level": "high",
                    "message": "폭염주의보",
                    "description": f"기온이 {weather['temperature']}℃로 매우 높습니다."
                })
            elif weather["temperature"] < -10:
                alerts.append({
                    "type": "cold_warning", 
                    "level": "high",
                    "message": "한파주의보",
                    "description": f"기온이 {weather['temperature']}℃로 매우 낮습니다."
                })
            
            if weather["humidity"] > 80:
                alerts.append({
                    "type": "humidity_warning",
                    "level": "medium", 
                    "message": "습도주의보",
                    "description": f"습도가 {weather['humidity']}%로 높습니다."
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"날씨 경보 조회 실패: {e}")
            return []
    
    async def get_weather_summary(self, location: Optional[str] = None) -> str:
        """
        날씨 정보를 간단한 텍스트로 요약
        
        Args:
            location: 위치
        
        Returns:
            날씨 요약 텍스트
        """
        try:
            weather = await self.get_current_weather(location)
            alerts = await self.get_weather_alerts(location)
            
            summary = f"{weather['location']} 현재 {weather['temperature']}℃, {weather['description']}, 습도 {weather['humidity']}%"
            
            if alerts:
                alert_messages = [alert["message"] for alert in alerts]
                summary += f" ({', '.join(alert_messages)})"
            
            return summary
            
        except Exception as e:
            logger.error(f"날씨 요약 생성 실패: {e}")
            return "날씨 정보를 가져올 수 없습니다."
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """모의 날씨 데이터 반환 (API 키가 없을 때)"""
        return {
            "location": "Seoul",
            "country": "KR",
            "temperature": 28.1,
            "feels_like": 31.2,
            "humidity": 62,
            "pressure": 1013,
            "description": "맑음",
            "main": "Clear",
            "wind_speed": 2.1,
            "visibility": 10.0,
            "timestamp": datetime.now().isoformat(),
            "source": "mock_data"
        }


# MCP 서버 인스턴스
weather_mcp_server = WeatherMCPServer()


# MCP 프로토콜 인터페이스
class WeatherMCPInterface:
    """MCP 프로토콜을 따르는 Weather 인터페이스"""
    
    def __init__(self):
        self.server = weather_mcp_server
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP 도구 호출
        
        Args:
            tool_name: 호출할 도구 이름
            arguments: 도구 인수
        
        Returns:
            도구 실행 결과
        """
        try:
            if tool_name == "get_current_weather":
                location = arguments.get("location")
                result = await self.server.get_current_weather(location)
                return {
                    "success": True,
                    "data": result,
                    "tool": tool_name
                }
            
            elif tool_name == "get_weather_alerts":
                location = arguments.get("location")
                result = await self.server.get_weather_alerts(location)
                return {
                    "success": True,
                    "data": result,
                    "tool": tool_name
                }
            
            elif tool_name == "get_weather_summary":
                location = arguments.get("location")
                result = await self.server.get_weather_summary(location)
                return {
                    "success": True,
                    "data": result,
                    "tool": tool_name
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "tool": tool_name
                }
                
        except Exception as e:
            logger.error(f"MCP 도구 호출 실패: {tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def get_available_tools(self) -> list:
        """사용 가능한 도구 목록 반환"""
        return [
            {
                "name": "get_current_weather",
                "description": "현재 날씨 정보 조회",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "위치 (예: Seoul,KR)"
                        }
                    }
                }
            },
            {
                "name": "get_weather_alerts", 
                "description": "날씨 경보 정보 조회",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "위치 (예: Seoul,KR)"
                        }
                    }
                }
            },
            {
                "name": "get_weather_summary",
                "description": "날씨 정보 요약",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "위치 (예: Seoul,KR)"
                        }
                    }
                }
            }
        ]


# MCP 인터페이스 인스턴스
weather_mcp_interface = WeatherMCPInterface()
