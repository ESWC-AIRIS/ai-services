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
            "DEVICE_WASHER": "washer"
        }
        return mapping.get(gateway_device_type, "unknown")
    
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
            1. 반드시 get_user_devices() 도구를 먼저 호출하여 실제 기기 목록을 확인하세요!
            2. 반드시 get_current_weather() 도구를 호출하여 날씨 정보를 확인하세요!
            3. 추천할 기기를 선택한 후 반드시 get_device_state(device_id)로 기기 상태를 확인하세요!
            4. device_id는 반드시 실제 사용자 기기 목록에서 가져온 ID만 사용하세요!
            5. device_id가 None이거나 빈 값이면 절대 추천을 생성하지 마세요!
            6. 도구를 사용하지 않고 추천을 생성하면 안 됩니다!
            
            사용 가능한 도구:
            - get_current_weather: 현재 날씨 조회 (필수)
            - get_user_devices: 사용자 스마트 가전 목록 조회 (필수)
            - get_device_state: 특정 기기 상태 조회 (필수 - 추천할 기기 선택 후 반드시 호출!)
            
            추천 워크플로우 (반드시 순서대로 실행):
            1. get_current_weather("Seoul") 호출하여 날씨 확인
            2. get_user_devices() 호출하여 사용자 기기 목록 확인 (필수!)
            3. 추천할 기기를 선택한 후 get_device_state(device_id)로 해당 기기 상태 확인 (필수!)
            4. 기기 상태에 따라 적절한 액션 선택:
               - 기기가 꺼져있으면(is_running=false): 먼저 켜기 액션을 첫 번째로 추가 (purifier_on, aircon_on)
               - 기기가 켜져있으면(is_running=true): 세부 설정 액션만 추가 (wind_power, temp_24 등)
            5. 날씨와 기기 정보를 종합하여 최적의 추천 생성
            6. device_id는 반드시 실제 사용자 기기 목록에서 가져온 ID 사용!
            
            ⚠️ 도구를 사용하지 않고 추천을 생성하면 안 됩니다!
            
            응답 형식 (JSON):
            {{
                "title": "추천 제목",
                "contents": "추천 내용",
                "device_control": {{
                    "device_type": "air_purifier|air_conditioner",
                    "device_id": "실제 기기 ID",
                    "actions": [
                        {{
                            "action": "액션명",
                            "order": 1,
                            "description": "액션 설명"
                        }}
                    ]
                }}
            }}
            
             ⚠️ 액션 시퀀스 생성 규칙:
             - 반드시 get_device_state로 기기 상태를 먼저 확인하세요
             - 기기가 꺼져있으면(is_running=false) 반드시 먼저 켜기 액션을 추가하세요 (purifier_on, aircon_on)
             - 기기가 켜져있으면(is_running=true) 세부 설정 액션만 추가하세요 (wind_power, temp_24 등)
             - 요청된 기능에 필요한 모든 액션을 순서대로 배열에 추가하세요
             - 타이머나 알림이 필요하면 마지막에 추가하세요
             - order는 1부터 순차적으로 설정하세요
             - 각 액션의 목적을 description에 명확히 설명하세요
             - delay_seconds는 기본 3초로 설정 (기기 제어 간 충분한 간격 필요)
            
            기기별 제어 액션 (실제 하드웨어 명세서 기반):
            
            🔹 공기청정기:
            - 작동 제어: purifier_on, purifier_off
            - 바람 세기: wind_low, wind_mid, wind_high, wind_auto, wind_power(파워모드)
            - 실행 모드: circulator(터보), clean(청정), auto
            
            🔹 에어컨:
            - 작동 제어: aircon_on, aircon_off
            - 바람 세기: aircon_wind_low, aircon_wind_mid, aircon_wind_high, aircon_wind_auto
            - 온도 설정: temp_{{n}} (예: temp_18, temp_19, temp_20... temp_30)
            - 실행 모드: aircon_dry(제습), aircon_clean(청정), aircon_cool(냉방)
            
            
            ⚠️ 기기 상태별 액션 선택 가이드:
            
            📱 공기청정기 상태별 추천:
            - is_running=false: 반드시 purifier_on 먼저 (기기 켜기)
            - is_running=true: wind_low/mid/high/auto/power (바람 세기 조정), circulator/clean/auto (실행 모드 선택)
            
            🌡️ 에어컨 상태별 추천:
            - is_running=false: 반드시 aircon_on 먼저 (기기 켜기)
            - is_running=true: temp_18~30 (온도 조정), aircon_wind_low/mid/high/auto (바람 세기 조정), aircon_dry/clean/cool (실행 모드 선택)
            
            
            ⚠️ 중요: device_id는 사용자 기기 목록에서 동적으로 가져와야 합니다!
            
            ⚠️ 매우 중요한 규칙:
            1. get_user_devices()를 반드시 호출하여 실제 기기 목록을 확인하세요!
            2. device_id는 반드시 실제 사용자 기기 목록에서 가져온 ID만 사용하세요!
            3. 사용자가 보유하지 않은 기기는 절대 추천하지 마세요!
            4. 한 번에 하나의 가전만 제어하세요!
            5. 가장 우선순위가 높은 기기 하나만 선택하여 추천하세요!
            
            {input}
            
            ⚠️ 반드시 다음 순서로 실행하세요:
            1. 먼저 get_user_devices() 도구를 호출하세요!
            2. 그 다음 get_current_weather("Seoul") 도구를 호출하세요!
            3. 추천할 기기를 선택한 후 get_device_state(device_id)로 상태를 확인하세요!
            4. 기기 상태(is_running)에 따라 필요한 액션 시퀀스를 생성하세요!
               - 꺼져있으면: 켜기 액션 먼저 + 세부 설정 액션
               - 켜져있으면: 세부 설정 액션만
            5. 마지막에 추천을 생성하세요!
            
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
                
                device_control_data = data.get("device_control", {})
                
                # actions 배열이 있으면 그대로 사용, 없으면 기존 방식으로 변환
                if "actions" in device_control_data:
                    # 새로운 actions 배열 방식
                    device_control = device_control_data
                else:
                    # 기존 단일 action 방식 (하위 호환성)
                    device_control = {
                        "device_type": device_control_data.get("device_type", "air_conditioner"),
                        "action": device_control_data.get("action", "turn_on"),
                        "device_id": device_control_data.get("device_id")
                    }
                
                return {
                    "title": data.get("title", "스마트 홈 추천"),
                    "contents": data.get("contents", "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."),
                    "device_control": device_control
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
        """동기 버전의 추천 생성 (데모용) - 이벤트 루프 충돌 방지"""
        import asyncio
        import concurrent.futures
        import threading
        
        def run_in_isolated_thread():
            """완전히 격리된 스레드에서 실행"""
            try:
                # 새로운 이벤트 루프 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.generate_recommendation(context))
                finally:
                    loop.close()
            except Exception as e:
                print(f"❌ 격리된 스레드에서 실행 실패: {e}")
                return {
                    "title": "데모 추천",
                    "contents": "데모용 추천입니다.",
                    "device_control": {
                        "device_type": "air_conditioner",
                        "action": "turn_on"
                    }
                }
        
        try:
            # 완전히 새로운 스레드에서 실행하여 이벤트 루프 충돌 완전 방지
            result = None
            exception = None
            
            def target():
                nonlocal result, exception
                try:
                    result = run_in_isolated_thread()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout=30)  # 30초 타임아웃
            
            if exception:
                raise exception
            
            if result is None:
                raise TimeoutError("추천 생성 타임아웃")
                
            return result
            
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
async def demo_generate_recommendation(scenario: str = None) -> Dict[str, Any]:
    """데모용 추천 생성 (시나리오 기반) - MongoDB 저장 포함"""
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
            recommendation = _generate_recommendation_from_weather(weather_data, scenario)
            
            # MongoDB에 저장
            recommendation_id = await _save_recommendation_to_mongodb(recommendation, mode="demo")
            
            # recommendation_id를 recommendation에 추가
            recommendation['recommendation_id'] = recommendation_id
            
            return recommendation
        
        # 기본 응답
        print(f"📊 기본 날씨 데이터: {default_weather}")
        recommendation = _generate_recommendation_from_weather(default_weather, "일반적인 날씨")
        
        # MongoDB에 저장
        recommendation_id = await _save_recommendation_to_mongodb(recommendation, mode="demo")
        
        # recommendation_id를 recommendation에 추가
        recommendation['recommendation_id'] = recommendation_id
        
        return recommendation
        
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
    """날씨 데이터를 기반으로 AI Agent가 추천 생성 (진짜 AI 사용)"""
    temp = weather_data["temperature"]
    feels_like = weather_data["feels_like"]
    humidity = weather_data["humidity"]
    description = weather_data["description"]
    
    # AI Agent에게 상황을 전달하여 추천 생성
    context = f"""
    시나리오: {scenario_name}
    현재 날씨 상황:
    - 기온: {temp}°C
    - 체감온도: {feels_like}°C  
    - 습도: {humidity}%
    - 날씨 설명: {description}
    
    이 상황에 맞는 스마트 홈 기기 제어를 추천해주세요.
    사용 가능한 기기와 액션은 프롬프트에 명시된 대로 사용하세요.
    """
    
    try:
        # 진짜 AI Agent 사용 - 동기 방식으로 직접 실행
        # 이벤트 루프 충돌을 피하기 위해 새로운 스레드에서 실행
        
        import threading
        import queue
        import time
        
        def run_ai_agent_thread():
            """별도 스레드에서 AI Agent 실행"""
            try:
                # 새로운 이벤트 루프 생성
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # AI Agent 생성 및 실행
                    agent = RecommendationAgent()
                    recommendation = agent.generate_recommendation_sync(context)
                    result_queue.put(recommendation)
                finally:
                    loop.close()
            except Exception as e:
                result_queue.put({
                    "title": "AI 추천 실패",
                    "contents": f"AI 추천 생성 중 오류: {e}",
                    "device_control": None
                })
        
        # 결과를 받을 큐 생성
        result_queue = queue.Queue()
        
        # 별도 스레드에서 AI Agent 실행
        thread = threading.Thread(target=run_ai_agent_thread)
        thread.daemon = True
        thread.start()
        
        # 결과 대기 (최대 60초)
        try:
            recommendation = result_queue.get(timeout=60)
            if recommendation and recommendation.get("device_control"):
                return recommendation
            else:
                raise Exception("AI Agent가 유효한 추천을 생성하지 못함")
        except queue.Empty:
            raise Exception("AI Agent 실행 타임아웃")
                
    except Exception as e:
        print(f"❌ AI Agent 추천 생성 실패: {e}")
    
    # AI Agent 실패 시 기본 응답
    return {
        "title": f"{scenario_name} - 스마트 홈 추천",
        "contents": f"현재 서울 기온 {temp}°C, 습도 {humidity}%입니다. 실내 환경 개선을 위한 스마트 홈 기기 제어를 추천합니다.",
        "device_control": {
            "device_type": "air_purifier",
            "action": "auto",
            "device_id": None  # 실제 기기 ID는 동적으로 조회해야 함
        }
    }

async def _save_recommendation_to_mongodb(recommendation: Dict[str, Any], mode: str = "demo") -> str:
    """추천을 MongoDB에 저장"""
    try:
        from app.core.database import get_database
        from app.services.recommendation_service import RecommendationService
        
        db = await get_database()
        recommendation_service = RecommendationService(db)
        
        # device_control에서 정보 추출 및 변환
        device_control_data = recommendation.get("device_control", {})
        
        # DeviceControl 객체로 변환 (actions 배열 지원)
        from app.models.recommendations import DeviceControl, DeviceAction
        
        if "actions" in device_control_data:
            # 새로운 actions 배열 방식
            actions = []
            for action_data in device_control_data.get("actions", []):
                action = DeviceAction(
                    action=action_data.get("action"),
                    order=action_data.get("order", 1),
                    description=action_data.get("description"),
                    delay_seconds=action_data.get("delay_seconds", 3)
                )
                actions.append(action)
            
            device_control = DeviceControl(
                device_type=device_control_data.get("device_type"),
                device_id=device_control_data.get("device_id"),
                actions=actions
            )
        else:
            # 기존 단일 action 방식 (하위 호환성)
            device_control = DeviceControl(
                device_type=device_control_data.get("device_type", "air_conditioner"),
                action=device_control_data.get("action", "turn_on"),
                device_id=device_control_data.get("device_id")
            )
        
        recommendation_id = await recommendation_service.create_recommendation(
            title=recommendation.get("title", "AI 추천"),
            contents=recommendation.get("contents", "AI가 생성한 추천입니다."),
            device_control=device_control,
            user_id="demo_user",
            mode=mode
        )
        
        print(f"✅ MongoDB에 추천 저장 완료: {recommendation_id}")
        return recommendation_id
        
    except Exception as e:
        print(f"❌ MongoDB 저장 실패: {e}")
        return None

async def demo_test_agent():
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
        recommendation = await demo_generate_recommendation("데모 테스트용 추천")
        
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
