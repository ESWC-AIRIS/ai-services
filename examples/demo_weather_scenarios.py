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
                    
                    # AI 서버가 Hardware 서버와 통신하여 사용자 응답을 받음
                    print(f"\n🔄 AI 서버가 Hardware 서버와 통신 중...")
                    print(f"📡 사용자 응답을 Hardware 서버에서 받습니다...")
                    
                    # AI 서버가 이미 Hardware 서버와 통신하여 제어까지 완료했음
                    if result.get('device_control'):
                        device_info = result['device_control']
                        print(f"🎯 제어 정보: {device_info.get('device_alias')} -> {device_info.get('action')}")
                        print(f"✅ AI 서버가 Hardware 서버를 통해 사용자 응답을 받고 실제 Gateway로 기기 제어를 완료했습니다!")
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
