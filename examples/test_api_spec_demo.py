"""
GazeHome AI Services - API 명세서 데모 테스트
명세서에 맞는 API 엔드포인트들을 테스트하는 데모 코드

실행 방법:
    PYTHONPATH=. python examples/test_api_spec_demo.py
"""
import asyncio
import httpx
import json
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 기존 .env 환경변수 사용 (하드코딩 제거)
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
GATEWAY_URL = os.getenv("GATEWAY_URL") 
HARDWARE_URL = os.getenv("HARDWARE_URL")

KST = pytz.timezone('Asia/Seoul')


class APISpecDemo:
    """API 명세서 데모 테스터"""
    
    def __init__(self):
        self.ai_server_url = AI_SERVER_URL
        self.gateway_url = GATEWAY_URL
        self.hardware_url = HARDWARE_URL
        self.test_results = []
    
    async def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ai_server_url}/health", timeout=10.0)
                if response.status_code == 200:
                    print(f"✅ AI 서버 연결 성공: {self.ai_server_url}")
                    return True
                else:
                    print(f"❌ AI 서버 연결 실패: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ AI 서버 연결 실패: {e}")
            return False
    
    async def test_lg_control_api(self) -> bool:
        """1. POST /api/lg/control 테스트 (HW → AI → Gateway)"""
        print('\n' + '='*60)
        print('1️⃣  LG 제어 API 테스트 (HW → AI → Gateway)')
        print('='*60)
        
        test_cases = [
            {
                "name": "공기청정기 켜기",
                "request": {"device_id": "b403_air_purifier_001", "action": "turn_on"},
                "expected": "[AI] 스마트 기기 단순 제어 완료"
            },
            {
                "name": "공기청정기 끄기", 
                "request": {"device_id": "b403_air_purifier_001", "action": "turn_off"},
                "expected": "[AI] 스마트 기기 단순 제어 완료"
            },
            {
                "name": "공기청정기 청소 모드",
                "request": {"device_id": "b403_air_purifier_001", "action": "clean"},
                "expected": "[AI] 스마트 기기 단순 제어 완료"
            },
            {
                "name": "공기청정기 자동 모드",
                "request": {"device_id": "b403_air_purifier_001", "action": "auto"},
                "expected": "[AI] 스마트 기기 단순 제어 완료"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f'\n📋 테스트 {i}: {test_case["name"]}')
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.ai_server_url}/api/lg/control",
                        json=test_case["request"],
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("message") == test_case["expected"]:
                            print(f"  ✅ 성공: {result['message']}")
                            results.append(True)
                        else:
                            print(f"  ❌ 응답 불일치: {result}")
                            results.append(False)
                    else:
                        print(f"  ❌ HTTP 오류: {response.status_code}")
                        print(f"  응답: {response.text}")
                        results.append(False)
                        
            except Exception as e:
                print(f"  ❌ 테스트 실패: {e}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        print(f'\n📊 LG 제어 API 결과: {success_count}/{total_count} 성공')
        return success_count == total_count
    
    async def test_recommendations_api(self) -> bool:
        """2. POST /api/recommendations 테스트 (AI → HW)"""
        print('\n' + '='*60)
        print('2️⃣  추천 API 테스트 (AI → HW)')
        print('='*60)
        
        test_cases = [
            {
                "name": "에어컨 추천",
                "request": {
                    "title": "에어컨 킬까요?",
                    "contents": "현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다."
                },
                "expected_confirm": "YES"
            },
            {
                "name": "조명 추천",
                "request": {
                    "title": "조명 끌까요?",
                    "contents": "저녁 시간이므로 조명을 끄고 휴식을 취하시는 것을 추천드립니다."
                },
                "expected_confirm": "NO"
            },
            {
                "name": "TV 추천",
                "request": {
                    "title": "TV 켤까요?",
                    "contents": "주말 오후이므로 TV를 켜고 영화를 보시는 것을 추천드립니다."
                },
                "expected_confirm": "YES"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f'\n📋 테스트 {i}: {test_case["name"]}')
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.ai_server_url}/api/recommendations/",
                        json=test_case["request"],
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("message") == "추천 문구 유저 피드백":
                            print(f"  ✅ 성공: {result['message']}")
                            print(f"  📝 사용자 응답: {result['confirm']}")
                            results.append(True)
                        else:
                            print(f"  ❌ 응답 불일치: {result}")
                            results.append(False)
                    else:
                        print(f"  ❌ HTTP 오류: {response.status_code}")
                        print(f"  응답: {response.text}")
                        results.append(False)
                        
            except Exception as e:
                print(f"  ❌ 테스트 실패: {e}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        print(f'\n📊 추천 API 결과: {success_count}/{total_count} 성공')
        return success_count == total_count
    
    async def test_integration_scenario(self) -> bool:
        """통합 시나리오 테스트"""
        print('\n' + '='*60)
        print('3️⃣  통합 시나리오 테스트')
        print('='*60)
        
        scenarios = [
            {
                "name": "시나리오 1: 직접 제어",
                "description": "사용자가 직접 공기청정기를 켜는 경우",
                "steps": [
                    ("HW → AI", "POST /api/lg/control", {"device_id": "b403_air_purifier_001", "action": "turn_on"})
                ]
            },
            {
                "name": "시나리오 2: AI 추천 기반 제어",
                "description": "AI가 추천하고 사용자가 허가한 후 제어하는 경우",
                "steps": [
                    ("AI → HW", "POST /api/recommendations/", {
                        "title": "에어컨 킬까요?",
                        "contents": "현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다."
                    }),
                    ("HW → AI", "POST /api/lg/control", {"device_id": "b403_ac_001", "action": "turn_on"})
                ]
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            print(f'\n🎬 {scenario["name"]}')
            print(f'📝 {scenario["description"]}')
            
            scenario_success = True
            
            for step_name, endpoint, data in scenario["steps"]:
                print(f'\n  🔄 {step_name}: {endpoint}')
                try:
                    # endpoint에서 "POST " 제거
                    clean_endpoint = endpoint.replace("POST ", "")
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.ai_server_url}{clean_endpoint}",
                            json=data,
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"    ✅ 성공: {result.get('message', 'OK')}")
                        else:
                            print(f"    ❌ 실패: {response.status_code}")
                            scenario_success = False
                            break
                            
                except Exception as e:
                    print(f"    ❌ 오류: {e}")
                    scenario_success = False
                    break
            
            results.append(scenario_success)
            print(f'  📊 시나리오 결과: {"✅ 성공" if scenario_success else "❌ 실패"}')
        
        success_count = sum(results)
        total_count = len(results)
        print(f'\n📊 통합 시나리오 결과: {success_count}/{total_count} 성공')
        return success_count == total_count
    
    async def run_demo(self):
        """전체 데모 실행"""
        print('\n' + '='*60)
        print('🚀 GazeHome AI API 명세서 데모')
        print('='*60)
        print(f'⏰ 시작 시간: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')
        print(f'🌐 AI 서버: {self.ai_server_url}')
        print(f'🌐 Gateway: {self.gateway_url}')
        print(f'🌐 Hardware: {self.hardware_url}')
        
        # 1. 서버 연결 테스트
        print('\n' + '='*60)
        print('0️⃣  서버 연결 테스트')
        print('='*60)
        
        if not await self.test_server_connection():
            print("❌ AI 서버 연결 실패로 데모 중단")
            return
        
        # 2. API 테스트들
        results = []
        
        # LG 제어 API 테스트
        results.append(await self.test_lg_control_api())
        
        # 추천 API 테스트
        results.append(await self.test_recommendations_api())
        
        # 통합 시나리오 테스트
        results.append(await self.test_integration_scenario())
        
        # 최종 결과
        print('\n' + '='*60)
        print('📊 데모 결과 요약')
        print('='*60)
        
        success_count = sum(results)
        total_count = len(results)
        
        if success_count == total_count:
            print('\n🎉 모든 테스트 통과!')
            print('  ✅ LG 제어 API (HW → AI → Gateway)')
            print('  ✅ 추천 API (AI → HW)')
            print('  ✅ 통합 시나리오')
            print('\n🚀 API 명세서에 맞는 시스템이 정상 작동합니다!')
        else:
            print(f'\n⚠️  일부 테스트 실패 ({success_count}/{total_count})')
            print('위의 오류 메시지를 확인해주세요.')
        
        print(f'\n⏰ 완료 시간: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')


async def main():
    """메인 데모 실행"""
    demo = APISpecDemo()
    await demo.run_demo()


if __name__ == '__main__':
    asyncio.run(main())
