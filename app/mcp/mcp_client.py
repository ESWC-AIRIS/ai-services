"""
GazeHome AI Services - MCP Client
MCP 서버들과 통신하는 클라이언트
"""

import logging
from typing import Dict, Any, Optional, List
from app.mcp.weather_mcp_server import weather_mcp_interface

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP 서버들과 통신하는 클라이언트"""
    
    def __init__(self):
        """MCP 클라이언트 초기화"""
        self.interfaces = {
            "weather": weather_mcp_interface
        }
        logger.info("MCP Client 초기화 완료")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        MCP 서버의 도구 호출
        
        Args:
            server_name: 서버 이름 (예: "weather")
            tool_name: 도구 이름
            arguments: 도구 인수
        
        Returns:
            도구 실행 결과
        """
        try:
            if server_name not in self.interfaces:
                return {
                    "success": False,
                    "error": f"Unknown server: {server_name}",
                    "server": server_name,
                    "tool": tool_name
                }
            
            interface = self.interfaces[server_name]
            result = await interface.call_tool(tool_name, arguments or {})
            
            logger.info(f"MCP 도구 호출: {server_name}.{tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"MCP 도구 호출 실패: {server_name}.{tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "server": server_name,
                "tool": tool_name
            }
    
    async def get_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        날씨 정보 조회 (편의 메서드)
        
        Args:
            location: 위치
        
        Returns:
            날씨 정보
        """
        result = await self.call_tool("weather", "get_current_weather", {"location": location})
        
        if result["success"]:
            return result["data"]
        else:
            logger.error(f"날씨 정보 조회 실패: {result['error']}")
            return {}
    
    async def get_weather_alerts(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        날씨 경보 조회 (편의 메서드)
        
        Args:
            location: 위치
        
        Returns:
            경보 정보 리스트
        """
        result = await self.call_tool("weather", "get_weather_alerts", {"location": location})
        
        if result["success"]:
            return result["data"]
        else:
            logger.error(f"날씨 경보 조회 실패: {result['error']}")
            return []
    
    async def get_weather_summary(self, location: Optional[str] = None) -> str:
        """
        날씨 요약 조회 (편의 메서드)
        
        Args:
            location: 위치
        
        Returns:
            날씨 요약 텍스트
        """
        result = await self.call_tool("weather", "get_weather_summary", {"location": location})
        
        if result["success"]:
            return result["data"]
        else:
            logger.error(f"날씨 요약 조회 실패: {result['error']}")
            return "날씨 정보를 가져올 수 없습니다."
    
    def get_available_servers(self) -> List[str]:
        """사용 가능한 서버 목록 반환"""
        return list(self.interfaces.keys())
    
    def get_available_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        특정 서버의 사용 가능한 도구 목록 반환
        
        Args:
            server_name: 서버 이름
        
        Returns:
            도구 목록
        """
        if server_name not in self.interfaces:
            return []
        
        interface = self.interfaces[server_name]
        return interface.get_available_tools()


# MCP 클라이언트 인스턴스
mcp_client = MCPClient()
