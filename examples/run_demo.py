"""
GazeHome AI Services - 데모 실행기
사용자 친화적 데모 시스템

실행 방법:
    python examples/run_demo.py
"""

import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo_scheduler_test import DemoSchedulerTest
from demo_weather_scenarios import DemoWeatherScenarios

class IntegratedDemo:
    """통합 데모 클래스"""
    
    def __init__(self):
        self.scheduler_demo = DemoSchedulerTest()
        self.weather_demo = DemoWeatherScenarios()
    
    async def run_full_demo(self):
        """전체 데모 실행"""
        print("🎯 GazeHome AI Services - 스마트 홈 데모")
        print("=" * 60)
        print("30분 대기 없이 다양한 기상 조건에서 AI 추천을 즉시 시연합니다!")
        print("=" * 60)
        
        # 사용자 선택
        print("\n📋 실행할 데모를 선택하세요:")
        print("1. 스마트 홈 AI 추천 데모 (기상 + 시간대별 시나리오)")
        print("2. 종료")
        
        while True:
            try:
                choice = input("\n선택 (1-2): ").strip()
                
                if choice == "1":
                    await self.run_smart_home_demo()
                    break
                elif choice == "2":
                    print("👋 데모를 종료합니다.")
                    return
                else:
                    print("❌ 잘못된 선택입니다. 1-2 중에서 선택하세요.")
            except KeyboardInterrupt:
                print("\n👋 데모를 종료합니다.")
                return
    
    async def run_smart_home_demo(self):
        """통합 스마트 홈 AI 추천 데모 실행"""
        print("\n🏠 스마트 홈 AI 추천 데모 시작")
        print("=" * 50)
        print("다양한 기상 조건과 시간대에서 AI 추천을 시연합니다!")
        print("=" * 50)
        
        # 시나리오 선택 메뉴
        print("\n📋 시나리오를 선택하세요:")
        print("1. 기상 시나리오 (여름 폭염, 겨울 한파, 봄 황사, 여름 장마, 가을 환절기, 겨울 건조)")
        print("2. 시간대별 시나리오 (아침 7시, 점심 12시, 저녁 6시, 밤 10시)")
        print("3. 개별 시나리오 선택")
        print("4. 전체 시나리오 실행")
        
        while True:
            try:
                choice = input("\n선택 (1-4): ").strip()
                
                if choice == "1":
                    await self.run_weather_scenarios()
                    break
                elif choice == "2":
                    await self.run_time_scenarios()
                    break
                elif choice == "3":
                    await self.run_individual_scenarios()
                    break
                elif choice == "4":
                    await self.run_all_scenarios()
                    break
                else:
                    print("❌ 잘못된 선택입니다. 1-4 중에서 선택하세요.")
            except KeyboardInterrupt:
                print("\n👋 데모를 종료합니다.")
                return
        
        print("\n🎉 스마트 홈 AI 추천 데모 완료!")
        print("💡 다양한 기상 조건과 시간대에서 AI 추천을 시연했습니다!")
        print("🚀 Gateway에 등록된 실제 기기만 추천하는 스마트한 AI를 확인했습니다!")
    
    async def run_weather_scenarios(self):
        """기상 시나리오 실행"""
        print("\n🌤️ 기상 시나리오 테스트")
        print("=" * 40)
        await self.weather_demo.run_all_scenarios()
    
    async def run_time_scenarios(self):
        """시간대별 시나리오 실행"""
        print("\n🕐 시간대별 시나리오 테스트")
        print("=" * 40)
        await self.weather_demo.test_time_based_scenarios()
    
    async def run_individual_scenarios(self):
        """개별 시나리오 선택 실행"""
        print("\n🎯 개별 시나리오 선택")
        print("=" * 40)
        
        # 기상 시나리오 목록
        weather_scenarios = [
            {"name": "여름 폭염", "context": "현재 기온이 35도로 폭염주의보가 발령되었습니다. 실내 온도도 30도를 넘어서 매우 더운 상황입니다."},
            {"name": "겨울 한파", "context": "기온이 영하 10도까지 떨어져 한파주의보가 발령되었습니다. 실내 온도도 15도 이하로 추운 상황입니다."},
            {"name": "봄 황사", "context": "황사가 심하게 불어와 미세먼지 농도가 매우 나쁨 수준입니다. 실내 공기질도 좋지 않은 상황입니다."},
            {"name": "여름 장마", "context": "장마철로 습도가 80% 이상으로 매우 높습니다. 실내도 습하고 답답한 상황입니다."},
            {"name": "가을 환절기", "context": "환절기로 일교차가 크고 감기 환자가 많습니다. 실내 공기질 관리가 중요한 시기입니다."},
            {"name": "겨울 건조", "context": "겨울철로 습도가 30% 이하로 매우 건조합니다. 실내 공기도 건조해서 불쾌한 상황입니다."}
        ]
        
        # 시간대별 시나리오 목록
        time_scenarios = [
            {"name": "아침 7시", "context": "아침 7시, 출근 준비를 하고 있습니다. 실내 온도는 22도입니다."},
            {"name": "점심 12시", "context": "점심 12시, 실내 온도가 28도로 높아졌습니다. 점심 준비로 부엌이 더워졌습니다."},
            {"name": "저녁 6시", "context": "저녁 6시, 퇴근 후 집에 도착했습니다. 실내 온도는 26도입니다."},
            {"name": "밤 10시", "context": "밤 10시, 잠자리 준비를 하고 있습니다. 실내 온도는 24도입니다."}
        ]
        
        all_scenarios = weather_scenarios + time_scenarios
        
        print("\n📋 사용 가능한 시나리오:")
        for i, scenario in enumerate(all_scenarios, 1):
            print(f"{i}. {scenario['name']}")
        
        while True:
            try:
                choice = input(f"\n시나리오 선택 (1-{len(all_scenarios)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(all_scenarios):
                    selected_scenario = all_scenarios[choice_num - 1]
                    print(f"\n🎯 선택된 시나리오: {selected_scenario['name']}")
                    await self.weather_demo.test_weather_scenario(
                        selected_scenario['name'], 
                        selected_scenario['context']
                    )
                    break
                else:
                    print(f"❌ 잘못된 선택입니다. 1-{len(all_scenarios)} 중에서 선택하세요.")
            except (ValueError, KeyboardInterrupt):
                print("❌ 잘못된 입력입니다.")
                break
    
    async def run_all_scenarios(self):
        """전체 시나리오 실행"""
        print("\n🌤️ 기상 시나리오 테스트")
        print("=" * 40)
        await self.weather_demo.run_all_scenarios()
        
        print("\n" + "="*60)
        
        print("\n🕐 시간대별 시나리오 테스트")
        print("=" * 40)
        await self.weather_demo.test_time_based_scenarios()

async def main():
    """메인 함수"""
    demo = IntegratedDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    print("🎯 GazeHome AI Services - 스마트 홈 데모")
    print("=" * 50)
    print("30분 대기 없이 다양한 기상 조건에서 AI 추천을 즉시 시연합니다!")
    print("⚠️  주의: AI 서버가 실행 중인지 확인하세요!")
    print("   AI 서버: http://localhost:8000")
    print("   Mock 서버: http://localhost:9000, http://localhost:8080")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 데모를 종료합니다.")
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")
        print("💡 AI 서버가 실행 중인지 확인하세요.")
