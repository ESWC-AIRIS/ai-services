"""
GazeHome AI Services - Weather MCP 테스트 스크립트
Weather MCP Server와 MCP Client를 테스트합니다.
"""

import asyncio
import json
from app.mcp import mcp_client, weather_mcp_server


async def test_weather_mcp_server():
    """Weather MCP Server 직접 테스트"""
    print("=" * 60)
    print("Weather MCP Server 직접 테스트")
    print("=" * 60)
    
    # 1. 현재 날씨 조회
    print("\n1. 현재 날씨 조회")
    weather = await weather_mcp_server.get_current_weather("Seoul,KR")
    print(f"날씨 정보: {json.dumps(weather, indent=2, ensure_ascii=False)}")
    
    # 2. 날씨 경보 조회
    print("\n2. 날씨 경보 조회")
    alerts = await weather_mcp_server.get_weather_alerts("Seoul,KR")
    print(f"경보 정보: {json.dumps(alerts, indent=2, ensure_ascii=False)}")
    
    # 3. 날씨 요약
    print("\n3. 날씨 요약")
    summary = await weather_mcp_server.get_weather_summary("Seoul,KR")
    print(f"요약: {summary}")


async def test_mcp_client():
    """MCP Client 테스트"""
    print("\n" + "=" * 60)
    print("MCP Client 테스트")
    print("=" * 60)
    
    # 1. 사용 가능한 서버 목록
    print("\n1. 사용 가능한 서버 목록")
    servers = mcp_client.get_available_servers()
    print(f"서버 목록: {servers}")
    
    # 2. Weather 서버의 사용 가능한 도구 목록
    print("\n2. Weather 서버 도구 목록")
    tools = mcp_client.get_available_tools("weather")
    print(f"도구 목록: {json.dumps(tools, indent=2, ensure_ascii=False)}")
    
    # 3. MCP Client를 통한 날씨 조회
    print("\n3. MCP Client를 통한 날씨 조회")
    weather = await mcp_client.get_weather("Seoul,KR")
    print(f"날씨 정보: {json.dumps(weather, indent=2, ensure_ascii=False)}")
    
    # 4. MCP Client를 통한 날씨 경보 조회
    print("\n4. MCP Client를 통한 날씨 경보 조회")
    alerts = await mcp_client.get_weather_alerts("Seoul,KR")
    print(f"경보 정보: {json.dumps(alerts, indent=2, ensure_ascii=False)}")
    
    # 5. MCP Client를 통한 날씨 요약
    print("\n5. MCP Client를 통한 날씨 요약")
    summary = await mcp_client.get_weather_summary("Seoul,KR")
    print(f"요약: {summary}")


async def test_mcp_tool_calls():
    """MCP 도구 호출 테스트"""
    print("\n" + "=" * 60)
    print("MCP 도구 호출 테스트")
    print("=" * 60)
    
    # 1. get_current_weather 도구 호출
    print("\n1. get_current_weather 도구 호출")
    result = await mcp_client.call_tool(
        "weather", 
        "get_current_weather", 
        {"location": "Seoul,KR"}
    )
    print(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 2. get_weather_alerts 도구 호출
    print("\n2. get_weather_alerts 도구 호출")
    result = await mcp_client.call_tool(
        "weather", 
        "get_weather_alerts", 
        {"location": "Seoul,KR"}
    )
    print(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 3. get_weather_summary 도구 호출
    print("\n3. get_weather_summary 도구 호출")
    result = await mcp_client.call_tool(
        "weather", 
        "get_weather_summary", 
        {"location": "Seoul,KR"}
    )
    print(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 4. 존재하지 않는 도구 호출 (에러 테스트)
    print("\n4. 존재하지 않는 도구 호출 (에러 테스트)")
    result = await mcp_client.call_tool(
        "weather", 
        "unknown_tool", 
        {}
    )
    print(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")


async def test_llm_integration():
    """LLM 서비스와 MCP 통합 테스트"""
    print("\n" + "=" * 60)
    print("LLM 서비스와 MCP 통합 테스트")
    print("=" * 60)
    
    try:
        from app.services.llm_service import LLMService
        
        llm_service = LLMService()
        
        # 테스트용 기기 정보
        device_info = {
            "device_id": "ac_001",
            "device_type": "air_conditioner",
            "device_name": "거실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "current_state": {
                "is_on": False,
                "temperature": 24
            }
        }
        
        context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "location": "living_room"
        }
        
        print("\nLLM 서비스를 통한 추천 생성 (날씨 정보 포함)")
        recommendation = await llm_service.generate_device_recommendation(
            device_info, context
        )
        
        print(f"추천 결과: {json.dumps(recommendation, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"LLM 통합 테스트 실패: {e}")
        print("(GEMINI_API_KEY가 설정되지 않았을 수 있습니다)")


async def main():
    """메인 테스트 함수"""
    print("GazeHome Weather MCP 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. Weather MCP Server 직접 테스트
        await test_weather_mcp_server()
        
        # 2. MCP Client 테스트
        await test_mcp_client()
        
        # 3. MCP 도구 호출 테스트
        await test_mcp_tool_calls()
        
        # 4. LLM 통합 테스트
        await test_llm_integration()
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
