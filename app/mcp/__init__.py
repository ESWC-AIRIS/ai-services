"""
GazeHome AI Services - MCP (Model Context Protocol) Module
"""

from .weather_mcp_server import weather_mcp_server, weather_mcp_interface
from .mcp_client import mcp_client, MCPClient

__all__ = [
    "weather_mcp_server",
    "weather_mcp_interface", 
    "mcp_client",
    "MCPClient"
]
