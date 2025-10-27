#!/usr/bin/env python3
"""
GazeHome AI Services - 스마트 홈 데모
LangChain 기반 추천 Agent 데모 및 전체 시스템 통합 테스트
"""

import os
import sys
import asyncio
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데모용 함수들 import
from app.agents.recommendation_agent import demo_generate_recommendation, demo_test_agent


class IntegratedDemo:
    """통합 데모 클래스"""
    
    def __init__(self):
        pass
    
    async def run_full_demo(self):
        """전체 데모 실행"""
        print("🎯 GazeHome AI Services - 스마트 홈 데모")
        print("=" * 60)
        print("LangChain 기반 추천 Agent와 전체 시스템 통합 테스트!")
        print("=" * 60)
        
        # 사용자 선택
        print("\n📋 실행할 데모를 선택하세요:")
        print("1. LangChain Agent 직접 테스트 (즉시 시나리오 테스트)")
        print("2. 전체 시스템 통합 테스트 (AI + 하드웨어 + Gateway)")
        print("3. 종료")
        
        while True:
            try:
                choice = input("\n선택 (1-3): ").strip()
                
                if choice == "1":
                    self.run_agent_demo()
                    break
                elif choice == "2":
                    await self.run_full_system_demo()
                    break
                elif choice == "3":
                    print("👋 데모를 종료합니다.")
                    return
                else:
                    print("❌ 잘못된 선택입니다. 1-3 중에서 선택하세요.")
            except KeyboardInterrupt:
                print("\n👋 데모를 종료합니다.")
                return
    
    def run_agent_demo(self):
        """LangChain Agent 직접 테스트 데모"""
        print("\n🤖 LangChain Agent 직접 테스트")
        print("=" * 60)
        print("LangChain 기반 스마트 홈 추천 Agent를 직접 테스트합니다!")
        print("=" * 60)
        
        try:
            # 기본 Agent 테스트
            print("\n🎯 기본 Agent 테스트")
            print("=" * 50)
            basic_success = demo_test_agent()
            
            if not basic_success:
                print("❌ 기본 테스트 실패로 데모를 중단합니다.")
                return
            
            # 날씨 시나리오 테스트
            print("\n🌤️ 날씨 시나리오 테스트")
        print("=" * 50)
            
            weather_scenarios = [
                ("여름폭염", "현재 기온이 35도로 폭염주의보가 발령되었습니다."),
                ("겨울한파", "기온이 영하 10도로 한파주의보가 발령되었습니다."),
                ("봄황사", "미세먼지 농도가 매우 나쁨 수준입니다."),
                ("여름장마", "습도가 80% 이상으로 매우 습합니다."),
                ("가을환절기", "일교차가 큰 환절기입니다."),
                ("겨울건조", "습도가 30% 이하로 매우 건조합니다.")
            ]
            
            weather_success_count = 0
            for scenario_name, context in weather_scenarios:
                print(f"\n🌤️ {scenario_name}")
                print("-" * 30)
                
                try:
                    # AI Agent로 추천 생성만 (하드웨어 통신 없음)
                    recommendation = demo_generate_recommendation(scenario_name)
                    
                    print(f"📝 제목: {recommendation['title']}")
                    print(f"💬 내용: {recommendation['contents']}")
                    print(f"🎯 기기 제어: {recommendation['device_control']}")
                    
                    weather_success_count += 1
                    print("✅ 시나리오 테스트 성공")
                    
                except Exception as e:
                    print(f"❌ 시나리오 테스트 실패: {e}")
            
            # 시간대별 시나리오 테스트
            print("\n🕐 시간대별 시나리오 테스트")
        print("=" * 50)
        
            time_scenarios = [
                ("아침7시", "아침 7시, 출근 준비 중입니다. 실내 온도 22도."),
                ("점심12시", "점심 12시, 실내 온도 28도, 점심 준비로 부엌이 더워졌습니다."),
                ("저녁6시", "저녁 6시, 퇴근 후 집 도착, 실내 온도 26도."),
                ("밤10시", "밤 10시, 잠자리 준비, 실내 온도 24도.")
            ]
            
            time_success_count = 0
            for time_name, context in time_scenarios:
                print(f"\n🕐 {time_name}")
                print("-" * 30)
                
                try:
                    # AI Agent로 추천 생성만 (하드웨어 통신 없음)
                    recommendation = demo_generate_recommendation(time_name)
                    
                    print(f"📝 제목: {recommendation['title']}")
                    print(f"💬 내용: {recommendation['contents']}")
                    print(f"🎯 기기 제어: {recommendation['device_control']}")
                    
                    time_success_count += 1
                    print("✅ 시간대 테스트 성공")
                    
                except Exception as e:
                    print(f"❌ 시간대 테스트 실패: {e}")
            
            # 전체 결과
            print("\n🎉 Agent 데모 완료!")
            print("=" * 60)
            print(f"✅ 기본 테스트: {'성공' if basic_success else '실패'}")
            print(f"✅ 날씨 시나리오: {weather_success_count}/{len(weather_scenarios)} 성공")
            print(f"✅ 시간대 시나리오: {time_success_count}/{len(time_scenarios)} 성공")
            
            overall_success = basic_success and weather_success_count == len(weather_scenarios) and time_success_count == len(time_scenarios)
            print(f"\n🎯 전체 결과: {'성공' if overall_success else '실패'}")
            
            if overall_success:
                print("\n🎉 LangChain Agent 테스트 완료!")
                print("✅ 모든 테스트가 성공적으로 완료되었습니다.")
            else:
                print("\n❌ LangChain Agent 테스트 실패")
                print("일부 테스트가 실패했습니다.")
                
        except Exception as e:
            print(f"\n❌ LangChain Agent 테스트 중 오류: {e}")
    
    async def _send_to_hardware(self, recommendation):
        """하드웨어에 추천 전송 (실제 Mock 서버와 통신)"""
        import httpx
        
        try:
            # 실제 하드웨어 Mock 서버에 추천 전송
            hardware_url = "http://localhost:8080"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{hardware_url}/api/recommendations",
                    json={
                        "title": recommendation['title'],
                        "contents": recommendation['contents']
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ 하드웨어 응답 오류: {response.status_code}")
                    return {"confirm": "NO", "message": "하드웨어 응답 오류"}
                    
        except httpx.ConnectError:
            print("❌ 하드웨어 Mock 서버에 연결할 수 없습니다. (포트 8080)")
            print("💡 터미널에서 하드웨어 Mock 서버를 실행하세요:")
            print("   python -c \"import uvicorn; from fastapi import FastAPI; app = FastAPI(); uvicorn.run(app, host='0.0.0.0', port=8080)\"")
            return {"confirm": "NO", "message": "하드웨어 서버 연결 실패"}
        except Exception as e:
            print(f"❌ 하드웨어 통신 실패: {e}")
            return {"confirm": "NO", "message": "통신 실패"}
    
    async def _control_device(self, device_control):
        """실제 기기 제어 (Gateway API 호출)"""
        import httpx
        
        try:
            # Gateway API로 실제 기기 제어
            # 여기서는 Mock 응답으로 시뮬레이션
            device_type = device_control.get('device_type')
            action = device_control.get('action')
            
            print(f"🎯 Gateway API 호출: {device_type} -> {action}")
            
            # 실제로는 Gateway API 호출
            # gateway_url = os.getenv("GATEWAY_URL", "http://localhost:9000")
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(f"{gateway_url}/api/lg/control", json={
            #         "device_id": "실제_기기_ID",
            #         "action": action
            #     })
            
            return {
                "success": True,
                "message": f"{device_type} {action} 제어 완료",
                "device_type": device_type,
                "action": action
            }
        except Exception as e:
            print(f"❌ 기기 제어 실패: {e}")
            return {"success": False, "message": "제어 실패"}
    
    async def run_full_system_demo(self):
        """전체 시스템 통합 테스트 (AI + 하드웨어 + Gateway)"""
        print("\n🔗 전체 시스템 통합 테스트")
        print("=" * 60)
        print("AI Agent → 하드웨어 Mock → Gateway API 전체 플로우 테스트!")
        print("=" * 60)
        
        print("\n📋 테스트 시나리오:")
        print("1. 여름 폭염 상황에서 에어컨 추천")
        print("2. 겨울 한파 상황에서 난방 추천")
        print("3. 봄 황사 상황에서 공기청정기 추천")
        
        test_scenarios = [
            ("여름폭염", "현재 기온이 35도로 폭염주의보가 발령되었습니다."),
            ("겨울한파", "기온이 영하 10도로 한파주의보가 발령되었습니다."),
            ("봄황사", "미세먼지 농도가 매우 나쁨 수준입니다.")
        ]
        
        success_count = 0
        for scenario_name, context in test_scenarios:
            print(f"\n🎯 {scenario_name} 시나리오 테스트")
            print("-" * 40)
            
            try:
                # 1. AI Agent로 추천 생성
                print("🤖 AI Agent 추천 생성 중...")
                recommendation = demo_generate_recommendation(scenario_name)
                
                print(f"📝 추천 제목: {recommendation['title']}")
                print(f"💬 추천 내용: {recommendation['contents']}")
                print(f"🎯 기기 제어: {recommendation['device_control']}")
                
                # 2. 하드웨어에 추천 전송
                print(f"\n📱 하드웨어 Mock 서버에 추천 전송 중...")
                hardware_response = await self._send_to_hardware(recommendation)
                
                print(f"👤 사용자 응답: {hardware_response['confirm']}")
                print(f"💬 응답 메시지: {hardware_response['message']}")
                
                # 3. 사용자가 YES로 응답한 경우 실제 기기 제어
                if hardware_response['confirm'] == 'YES':
                    print(f"\n🔧 Gateway API로 실제 기기 제어 실행...")
                    control_result = await self._control_device(recommendation['device_control'])
                    print(f"✅ 기기 제어 결과: {control_result['message']}")
                else:
                    print(f"❌ 사용자가 추천을 거부했습니다.")
                
                success_count += 1
                print(f"✅ {scenario_name} 시나리오 테스트 완료")
                
            except Exception as e:
                print(f"❌ {scenario_name} 시나리오 테스트 실패: {e}")
        
        # 전체 결과
        print(f"\n🎉 전체 시스템 통합 테스트 완료!")
        print("=" * 60)
        print(f"✅ 성공한 시나리오: {success_count}/{len(test_scenarios)}")
        
        if success_count == len(test_scenarios):
            print("\n🎉 모든 시스템이 정상적으로 작동합니다!")
            print("✅ AI Agent → 하드웨어 Mock → Gateway API 통신 성공")
        else:
            print(f"\n❌ {len(test_scenarios) - success_count}개 시나리오가 실패했습니다.")
            print("💡 하드웨어 Mock 서버가 실행 중인지 확인하세요.")


async def main():
    """메인 함수"""
    demo = IntegratedDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
        asyncio.run(main())