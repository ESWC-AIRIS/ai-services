"""
GazeHome AI Services - 데모용 기상 시나리오 테스트
다양한 기상 조건에서 AI 추천 변화를 확인하는 데모 스크립트
"""

import asyncio
import httpx
import time
import json
from datetime import datetime
import pytz
from typing import Dict, Any

# AI 서버 설정
AI_SERVER_URL = "http://localhost:8000"

class DemoWeatherScenarios:
    """데모용 기상 시나리오 테스트 클래스"""
    
    def __init__(self):
        self.ai_server_url = AI_SERVER_URL
    
    async def test_weather_scenario(self, scenario_name: str, context: str):
        """특정 기상 시나리오 테스트"""
        print(f"\n🌤️ {scenario_name}")
        print("-" * 40)
        print(f"📝 상황: {context}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_server_url}/api/recommendations/",
                    json={
                        "title": f"{scenario_name} 추천",
                        "contents": context
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ AI 추천 생성 성공!")
                    print(f"💬 AI 응답: {result.get('message', 'N/A')}")
                    
                    # 실제 사용자 입력 받기
                    print(f"\n❓ 이 추천을 실행하시겠습니까?")
                    while True:
                        try:
                            user_input = input("YES/NO 입력: ").strip().upper()
                            if user_input in ["YES", "NO"]:
                                break
                            else:
                                print("❌ YES 또는 NO만 입력하세요.")
                        except KeyboardInterrupt:
                            user_input = "NO"
                            break
                    
                    print(f"👤 사용자 응답: {user_input}")
                    
                    # 사용자가 YES로 답한 경우 실제 기기 제어 실행
                    if user_input == "YES" and result.get('device_control'):
                        device_info = result['device_control']
                        print(f"🎯 제어 정보: {device_info.get('device_alias')} -> {device_info.get('action')}")
                        
                        # Gateway를 통한 실제 기기 제어
                        await self.execute_device_control(device_info)
                    elif user_input == "NO":
                        print("❌ 사용자가 추천을 거부했습니다.")
                    else:
                        print("⚠️ 제어할 기기 정보가 없습니다.")
                else:
                    print(f"❌ 추천 생성 실패: {response.status_code}")
                    print(f"오류: {response.text}")
                    
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {str(e)}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
        
        # 요청 간 간격 (서버 부하 방지)
        await asyncio.sleep(2)
    
    async def execute_device_control(self, device_info: Dict[str, Any]):
        """Gateway를 통한 실제 기기 제어 실행"""
        try:
            device_id = device_info.get('device_id')
            action = device_info.get('action')
            device_alias = device_info.get('device_alias')
            
            if not device_id or not action:
                print("❌ 기기 제어 정보가 불완전합니다.")
                return
            
            print(f"\n🔧 Gateway를 통한 기기 제어 실행:")
            print(f"  📱 기기: {device_alias} ({device_id})")
            print(f"  ⚡ 액션: {action}")
            print(f"  🔄 제어 중...")
            
            # Gateway 제어 API 호출
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:9000/api/lg/control",
                    json={
                        "device_id": device_id,
                        "action": action
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ {result.get('message', '기기 제어 완료')}")
                else:
                    print(f"  ❌ 기기 제어 실패: {response.status_code}")
                    print(f"  오류: {response.text}")
                    
        except Exception as e:
            print(f"❌ 기기 제어 실행 중 오류 발생: {e}")
    
    async def run_all_scenarios(self):
        """모든 기상 시나리오 실행"""
        print("🌤️ GazeHome AI Services - 기상 시나리오 데모")
        print("=" * 60)
        
        scenarios = [
            {
                "name": "여름 폭염",
                "context": "현재 기온이 35도로 폭염주의보가 발령되었습니다. 실내 온도도 30도를 넘어서 매우 더운 상황입니다."
            },
            {
                "name": "겨울 한파",
                "context": "기온이 영하 10도까지 떨어져 한파주의보가 발령되었습니다. 실내 온도도 15도 이하로 추운 상황입니다."
            },
            {
                "name": "봄 황사",
                "context": "황사가 심하게 불어와 미세먼지 농도가 매우 나쁨 수준입니다. 실내 공기질도 좋지 않은 상황입니다."
            },
            {
                "name": "여름 장마",
                "context": "장마철로 습도가 80% 이상으로 매우 높습니다. 실내도 습하고 답답한 상황입니다."
            },
            {
                "name": "가을 환절기",
                "context": "환절기로 일교차가 크고 감기 환자가 많습니다. 실내 공기질 관리가 중요한 시기입니다."
            },
            {
                "name": "겨울 건조",
                "context": "겨울철로 습도가 30% 이하로 매우 건조합니다. 실내 공기도 건조해서 불쾌한 상황입니다."
            }
        ]
        
        for scenario in scenarios:
            await self.test_weather_scenario(scenario["name"], scenario["context"])
            await asyncio.sleep(1)  # 1초 대기
    
    async def test_time_based_scenarios(self):
        """시간대별 시나리오 테스트"""
        print("\n🕐 시간대별 시나리오 테스트")
        print("=" * 40)
        
        time_scenarios = [
            {
                "time": "아침 7시",
                "context": "아침 7시, 출근 준비를 하고 있습니다. 실내 온도는 22도입니다."
            },
            {
                "time": "점심 12시",
                "context": "점심 12시, 실내 온도가 28도로 높아졌습니다. 점심 준비로 부엌이 더워졌습니다."
            },
            {
                "time": "저녁 6시",
                "context": "저녁 6시, 퇴근 후 집에 도착했습니다. 실내 온도는 26도입니다."
            },
            {
                "time": "밤 10시",
                "context": "밤 10시, 잠자리 준비를 하고 있습니다. 실내 온도는 24도입니다."
            }
        ]
        
        for scenario in time_scenarios:
            await self.test_weather_scenario(scenario["time"], scenario["context"])
            await asyncio.sleep(1)

async def main():
    """메인 데모 함수"""
    demo = DemoWeatherScenarios()
    
    print("🎯 GazeHome AI Services - 기상 시나리오 데모")
    print("=" * 60)
    
    # 1. 기상 시나리오 테스트
    await demo.run_all_scenarios()
    
    # 2. 시간대별 시나리오 테스트
    await demo.test_time_based_scenarios()
    
    print("\n🎉 기상 시나리오 데모 완료!")
    print("💡 팁: 다양한 기상 조건에서 AI가 어떻게 다른 추천을 하는지 확인했습니다.")

if __name__ == "__main__":
    asyncio.run(main())
