"""
GazeHome AI Services - Smart Recommendation Agent
LangChain 기반 스마트 홈 추천 Agent
"""

import asyncio
import os
import json
import aiohttp
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# LangChain imports
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
class WeatherTool:
    """날씨 도구"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"

class GatewayTool:
    """Gateway API 도구"""
    
    def __init__(self, gateway_url: str = None):
        self.gateway_url = gateway_url or os.getenv("GATEWAY_URL", "http://localhost:9000")
        self.devices_endpoint = f"{self.gateway_url}/api/lg/devices"
        self.device_state_endpoint = f"{self.gateway_url}/api/lg/devices"
    
    def _map_device_type(self, gateway_device_type: str) -> str:
        """Gateway 디바이스 타입을 표준 타입으로 매핑"""
        mapping = {
            "DEVICE_AIR_CONDITIONER": "air_conditioner",
            "DEVICE_AIR_PURIFIER": "air_purifier", 
            "DEVICE_WASHER": "washer",
            "DEVICE_DRYER": "dryer"
        }
        return mapping.get(gateway_device_type, gateway_device_type.lower())
    
    async def get_user_devices(self) -> str:
        """사용자의 스마트 가전 목록 조회"""
        try:
            print(f"🔍 Gateway API 호출 시도: {self.devices_endpoint}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.devices_endpoint) as response:
                    print(f"📡 Gateway API 응답 상태: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"📋 Gateway API 응답 데이터: {data}")
                        
                        devices = data.get('response', [])
                        
                        # 기기 정보를 간단한 형태로 정리
                        device_list = []
                        for device in devices:
                            device_info = device.get('deviceInfo', {})
                            
                            # Gateway API 응답 구조에 맞게 파싱
                            device_data = {
                                "device_id": device.get("deviceId"),
                                "device_name": device_info.get("modelName"),
                                "device_type": self._map_device_type(device_info.get("deviceType")),
                                "device_alias": device_info.get("alias"),
                                "is_online": device_info.get("reportable", False)
                            }
                            device_list.append(device_data)
                        
                        result = {
                            "total_devices": len(device_list),
                            "devices": device_list,
                            "source": "Gateway API"
                        }
                        print(f"✅ Gateway API 성공: {len(device_list)}개 기기 조회")
                        return json.dumps(result, ensure_ascii=False)
                    else:
                        print(f"❌ Gateway API 실패: {response.status}")
                        return f"기기 목록 조회 실패: {response.status}"
        except Exception as e:
            print(f"❌ Gateway API 예외 발생: {e}")
            return f"기기 목록 조회 실패: {e}"
    
    async def get_device_state(self, device_id: str) -> str:
        """특정 기기의 현재 상태 조회"""
        try:
            url = f"{self.device_state_endpoint}/{device_id}/state"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        state_info = {
                            "device_id": device_id,
                            "is_online": data.get("is_online", False),
                            "current_state": data.get("current_state", "UNKNOWN"),
                            "is_running": data.get("is_running", False),
                            "can_control": data.get("can_control", False)
                        }
                        return json.dumps(state_info, ensure_ascii=False)
                    else:
                        print(f"❌ 기기 상태 조회 실패: {response.status}")
                        return f"기기 상태 조회 실패: {response.status}"
        except Exception as e:
            print(f"❌ 기기 상태 조회 예외 발생: {e}")
            return f"기기 상태 조회 실패: {e}"
class WeatherTool:
    """날씨 도구"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, location: str = "Seoul,KR") -> str:
        """현재 날씨 조회"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_info = {
                            "location": data["name"],
                            "country": data["sys"]["country"],
                            "temperature": data["main"]["temp"],
                            "feels_like": data["main"]["feels_like"],
                            "humidity": data["main"]["humidity"],
                            "description": data["weather"][0]["description"],
                            "icon": data["weather"][0]["icon"]
                        }
                        return json.dumps(weather_info, ensure_ascii=False)
                    else:
                        return f"날씨 API 호출 실패: {response.status}"
        except Exception as e:
            return f"날씨 API 호출 실패: {e}"
    
    async def get_forecast(self, location: str = "Seoul,KR", days: int = 5) -> str:
        """날씨 예보 조회"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/forecast"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 3시간마다 데이터
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast_info = {
                            "location": data["city"]["name"],
                            "country": data["city"]["country"],
                            "forecasts": data["list"][:days]  # 첫 N일만
                        }
                        return json.dumps(forecast_info, ensure_ascii=False)
                    else:
                        return f"예보 API 호출 실패: {response.status}"
        except Exception as e:
            return f"예보 API 호출 실패: {e}"

class RecommendationAgent:
    """스마트 홈 추천 Agent"""
    
    def __init__(self):
        self.weather_tool = WeatherTool(os.getenv("WEATHER_API_KEY"))
        self.gateway_tool = GatewayTool()
        self.agent_executor = None
        self._setup_agent()
    
    def _get_user_devices_wrapper(self, *args, **kwargs):
        """사용자 기기 목록 조회 래퍼 함수 (동기)"""
        import asyncio
        try:
            # 이미 실행 중인 이벤트 루프가 있는지 확인
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 이미 실행 중인 루프가 있으면 새 스레드에서 실행
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.gateway_tool.get_user_devices())
                    return future.result()
            else:
                return asyncio.run(self.gateway_tool.get_user_devices())
        except RuntimeError:
            # 이벤트 루프가 없으면 새로 생성
            return asyncio.run(self.gateway_tool.get_user_devices())
    
    def _get_device_state_wrapper(self, device_id: str, *args, **kwargs):
        """기기 상태 조회 래퍼 함수 (동기)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.gateway_tool.get_device_state(device_id))
                    return future.result()
            else:
                return asyncio.run(self.gateway_tool.get_device_state(device_id))
        except RuntimeError:
            return asyncio.run(self.gateway_tool.get_device_state(device_id))
    
    def _setup_agent(self):
        """LangChain Agent 설정"""
        # Gemini 모델 설정
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7
        )
        
        # 동기 함수로 Tool 정의 (Gemini 호환성 개선)
        def get_current_weather_sync(location: str) -> str:
            """현재 날씨를 조회합니다. location은 '도시명,국가코드' 형식입니다 (예: 'Seoul,KR')."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 이미 실행 중인 루프가 있으면 새 스레드에서 실행
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.weather_tool.get_current_weather(location))
                        return future.result()
                else:
                    return asyncio.run(self.weather_tool.get_current_weather(location))
            except RuntimeError:
                return asyncio.run(self.weather_tool.get_current_weather(location))
        
        def get_user_devices_sync(*args, **kwargs) -> str:
            """사용자가 등록한 스마트 가전 목록을 조회합니다."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.gateway_tool.get_user_devices())
                        return future.result()
                else:
                    return asyncio.run(self.gateway_tool.get_user_devices())
            except RuntimeError:
                return asyncio.run(self.gateway_tool.get_user_devices())
        
        def get_device_state_sync(device_id: str, *args, **kwargs) -> str:
            """특정 기기의 현재 상태를 조회합니다. device_id는 기기의 고유 ID입니다."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.gateway_tool.get_device_state(device_id))
                        return future.result()
                else:
                    return asyncio.run(self.gateway_tool.get_device_state(device_id))
            except RuntimeError:
                return asyncio.run(self.gateway_tool.get_device_state(device_id))
        
        # Tool 정의
        all_tools = [
            Tool(
                name="get_current_weather",
                description="현재 날씨를 조회합니다. location은 '도시명,국가코드' 형식입니다 (예: 'Seoul,KR').",
                func=get_current_weather_sync
            ),
            Tool(
                name="get_user_devices",
                description="사용자가 등록한 스마트 가전 목록을 조회합니다.",
                func=get_user_devices_sync
            ),
            Tool(
                name="get_device_state",
                description="특정 기기의 현재 상태를 조회합니다. device_id는 기기의 고유 ID입니다.",
                func=get_device_state_sync
            )
        ]
        prompt = ChatPromptTemplate.from_messages([
            ("human", """
            당신은 GazeHome AI 추천 어시스턴트입니다.
            
            ⚠️ 매우 중요한 규칙:
            1. 상황에 따라 필요한 도구를 자율적으로 선택하여 사용하세요.
            2. 항상 날씨 정보를 먼저 확인하세요.
            3. 사용자 기기 목록을 확인하여 실제 보유 기기만 추천하세요.
            4. 필요시 특정 기기의 상태를 확인하세요.
            
            사용 가능한 도구:
            - get_current_weather: 현재 날씨 조회 (필수)
            - get_user_devices: 사용자 스마트 가전 목록 조회 (필수)
            - get_device_state: 특정 기기 상태 조회 (선택사항)
            
            추천 워크플로우:
            1. get_current_weather("Seoul") 호출하여 날씨 확인
            2. get_user_devices() 호출하여 사용자 기기 목록 확인
            3. 필요시 get_device_state(device_id)로 특정 기기 상태 확인
            4. 날씨와 기기 정보를 종합하여 최적의 추천 생성
            
            응답 형식 (JSON):
            {{
                "title": "추천 제목",
                "contents": "추천 내용",
                "device_control": {{
                    "device_type": "air_purifier|dryer|air_conditioner",
                    "action": "공기청정기: turn_on|turn_off|clean|auto, 건조기: dryer_on|dryer_off|dryer_start|dryer_stop, 에어컨: aircon_on|aircon_off|temp_24|temp_25|temp_26|temp_27|temp_28"
                }}
            }}
            
            기기별 제어 액션:
            - 공기청정기: turn_on(작동), turn_off(정지), clean(청정모드), auto(자동모드)
            - 건조기: dryer_on(작동), dryer_off(정지), dryer_start(시작), dryer_stop(중지)
            - 에어컨: aircon_on(작동), aircon_off(정지), temp_18~30(온도설정)
            
            중요: 
            1. 사용자가 보유하지 않은 기기는 절대 추천하지 마세요!
            2. 한 번에 하나의 가전만 제어하세요!
            3. 가장 우선순위가 높은 기기 하나만 선택하여 추천하세요!
            
            {input}
            
            {agent_scratchpad}
            """)
        ])
        
        # Agent 생성
        agent = create_tool_calling_agent(llm, all_tools, prompt)
        
        # Agent Executor 생성
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=all_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        print("✅ 스마트 추천 Agent 설정 완료")
    
    async def generate_recommendation(self, context: str = None) -> Dict[str, Any]:
        """추천 생성"""
        try:
            # Agent에게 추천 생성 요청
            prompt = f"""
            현재 상황에 맞는 스마트 홈 기기 제어를 추천해주세요.
            
            상황: {context or "일반적인 스마트 홈 환경"}
            
            필요한 도구를 자율적으로 선택하여 사용하세요.
            """
            
            # Agent 실행
            result = await self.agent_executor.ainvoke({"input": prompt})
            
            print(f"🔍 Agent 실행 결과: {result}")
            
            # 결과에서 추천 정보 추출
            response_text = result.get("output", "")
            
            # JSON 파싱 시도
            try:
                # 마크다운 코드 블록에서 JSON 추출
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # 코드 블록이 없으면 전체 문자열을 JSON으로 시도
                    json_str = response_text.strip()
                
                # JSON 파싱
                data = json.loads(json_str)
                
                return {
                    "title": data.get("title", "스마트 홈 추천"),
                    "contents": data.get("contents", "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."),
                    "device_control": data.get("device_control", {
                        "device_type": "air_conditioner",
                        "action": "turn_on"
                    })
                }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ JSON 파싱 실패: {e}")
                return {
                    "title": "스마트 홈 추천",
                    "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                    "device_control": {
                        "device_type": "air_conditioner",
                        "action": "turn_on"
                    }
                }
        
        except Exception as e:
            print(f"❌ 스마트 추천 Agent 추천 생성 실패: {e}")
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                "device_control": None
            }
    
    async def close(self):
        """리소스 정리"""
        pass
    
    def generate_recommendation_sync(self, context: str = None) -> Dict[str, Any]:
        """동기 버전의 추천 생성 (데모용)"""
        import asyncio
        import concurrent.futures
        
        def run_in_new_loop():
            """새로운 이벤트 루프에서 실행"""
            try:
                # 새로운 이벤트 루프 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.generate_recommendation(context))
                finally:
                    loop.close()
            except Exception as e:
                print(f"❌ 새 이벤트 루프에서 실행 실패: {e}")
                return {
                    "title": "데모 추천",
                    "contents": "데모용 추천입니다.",
                    "device_control": {
                        "device_type": "air_conditioner",
                        "action": "turn_on"
                    }
                }
        
        try:
            # 항상 새 스레드에서 실행하여 이벤트 루프 충돌 방지
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                return future.result(timeout=30)  # 30초 타임아웃
        except Exception as e:
            print(f"❌ 동기 추천 생성 실패: {e}")
            return {
                "title": "데모 추천",
                "contents": "데모용 추천입니다.",
                "device_control": {
                    "device_type": "air_conditioner",
                    "action": "turn_on"
                }
            }

# 전역 Agent 인스턴스
recommendation_agent = None

def create_agent():
    """추천 Agent 생성 (FastAPI 호환)"""
    return create_recommendation_agent()

def create_recommendation_agent():
    """추천 Agent 생성"""
    global recommendation_agent
    if recommendation_agent is None:
        recommendation_agent = RecommendationAgent()
    return recommendation_agent

# 데모용 간단한 함수들
def demo_generate_recommendation(scenario: str = None) -> Dict[str, Any]:
    """데모용 추천 생성 (시나리오 기반)"""
    try:
        import json
        import os
        
        # 데모 시나리오 JSON 파일 로드
        scenarios_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "examples", "demo_scenarios.json")
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            scenarios_data = json.load(f)
        
        demo_scenarios = scenarios_data["demo_scenarios"]
        default_weather = scenarios_data["default_weather"]
        
        # 시나리오명으로 직접 선택
        if scenario and scenario in demo_scenarios:
            weather_data = demo_scenarios[scenario]["weather_data"]
            print(f"🌤️ 데모 시나리오: {scenario}")
            print(f"📊 날씨 데이터: {weather_data}")
            
            # 실제 Agent처럼 날씨 데이터를 기반으로 추천 생성
            return _generate_recommendation_from_weather(weather_data, scenario)
        
        # 기본 응답
        print(f"📊 기본 날씨 데이터: {default_weather}")
        return _generate_recommendation_from_weather(default_weather, "일반적인 날씨")
        
    except Exception as e:
        print(f"❌ 데모 추천 생성 실패: {e}")
        return {
            "title": "데모 추천",
            "contents": "데모용 추천입니다.",
            "device_control": {
                "device_type": "air_conditioner",
                "action": "turn_on"
            }
        }

def _generate_recommendation_from_weather(weather_data: Dict[str, Any], scenario_name: str) -> Dict[str, Any]:
    """날씨 데이터를 기반으로 추천 생성"""
    temp = weather_data["temperature"]
    feels_like = weather_data["feels_like"]
    humidity = weather_data["humidity"]
    description = weather_data["description"]
    
    # 온도 기반 추천 로직
    if temp >= 30:
        return {
            "title": f"{scenario_name} - 에어컨 켜기 추천",
            "contents": f"현재 서울 기온이 {temp}°C로 매우 더운 상황입니다. 체감온도는 {feels_like}°C입니다. 실내 온도 조절을 위해 에어컨을 켜는 것을 추천합니다.",
            "device_control": {
                "device_type": "air_conditioner",
                "action": "aircon_on"
            }
        }
    elif temp <= 5:
        return {
            "title": f"{scenario_name} - 난방 기기 추천",
            "contents": f"현재 서울 기온이 {temp}°C로 매우 추운 상황입니다. 체감온도는 {feels_like}°C입니다. 실내 온도 조절을 위해 에어컨 난방을 켜는 것을 추천합니다.",
            "device_control": {
                "device_type": "air_conditioner",
                "action": "aircon_on"
            }
        }
    elif humidity >= 80:
        return {
            "title": f"{scenario_name} - 공기청정기 자동모드",
            "contents": f"현재 서울 습도가 {humidity}%로 매우 높습니다. 실내 공기 순환과 습도 조절을 위해 공기청정기 자동모드를 켜는 것을 추천합니다.",
            "device_control": {
                "device_type": "air_purifier",
                "action": "auto"
            }
        }
    elif humidity <= 30:
        return {
            "title": f"{scenario_name} - 공기청정기 가동",
            "contents": f"현재 서울 습도가 {humidity}%로 매우 건조합니다. 실내 공기 정화와 쾌적한 환경을 위해 공기청정기를 켜는 것을 추천합니다.",
            "device_control": {
                "device_type": "air_purifier",
                "action": "turn_on"
            }
        }
    elif "haze" in description or "dust" in description:
        return {
            "title": f"{scenario_name} - 공기청정기 필수",
            "contents": f"현재 서울에 황사나 미세먼지가 있어 공기질이 나쁜 상황입니다. 실내 공기 정화를 위해 공기청정기를 켜는 것을 강력히 추천합니다.",
            "device_control": {
                "device_type": "air_purifier",
                "action": "turn_on"
            }
        }
    else:
        return {
            "title": f"{scenario_name} - 공기청정기 추천",
            "contents": f"현재 서울 기온 {temp}°C, 습도 {humidity}%입니다. 실내 공기 정화를 위해 공기청정기를 켜는 것을 추천합니다.",
            "device_control": {
                "device_type": "air_purifier",
                "action": "turn_on"
            }
        }

def demo_test_agent():
    """데모용 Agent 테스트"""
    print("🎯 데모용 Agent 테스트 시작")
    print("=" * 50)
    
    try:
        # 환경변수 확인
        print(f"🌍 환경 설정:")
        print(f"  - GEMINI_API_KEY: {'설정됨' if os.getenv('GEMINI_API_KEY') else '미설정'}")
        print(f"  - WEATHER_API_KEY: {'설정됨' if os.getenv('WEATHER_API_KEY') else '미설정'}")
        print(f"  - GATEWAY_URL: {os.getenv('GATEWAY_URL', 'http://localhost:9000')}")
        
        # Agent 생성 테스트
        print("\n🔧 Agent 생성 테스트...")
        agent = create_recommendation_agent()
        print("✅ Agent 생성 성공")
        
        # 추천 생성 테스트
        print("\n🔧 추천 생성 테스트...")
        recommendation = demo_generate_recommendation("데모 테스트용 추천")
        
        print(f"\n📋 추천 결과:")
        print(f"  - 제목: {recommendation['title']}")
        print(f"  - 내용: {recommendation['contents']}")
        print(f"  - 기기 제어: {recommendation['device_control']}")
        
        print("\n✅ 데모 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데모 테스트 실패: {e}")
        return False

async def main():
    """테스트 함수"""
    print("=" * 60)
    print("스마트 추천 Agent 테스트")
    print("=" * 60)
    
    # 환경변수 확인
    print(f"🌍 환경 설정:")
    print(f"  - GEMINI_API_KEY: {'설정됨' if os.getenv('GEMINI_API_KEY') else '미설정'}")
    print(f"  - WEATHER_API_KEY: {'설정됨' if os.getenv('WEATHER_API_KEY') else '미설정'}")
    
    # Agent 생성
    agent = create_recommendation_agent()
    
    # 추천 생성 테스트
    print("\n🔧 추천 생성 테스트...")
    recommendation = await agent.generate_recommendation()
    
    print(f"\n📋 추천 결과:")
    print(f"  - 제목: {recommendation['title']}")
    print(f"  - 내용: {recommendation['contents']}")
    print(f"  - 기기 제어: {recommendation['device_control']}")
    
    # 정리
    await agent.close()
    print("\n✅ 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main())
