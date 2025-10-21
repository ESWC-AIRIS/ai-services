"""
GazeHome AI Services - MVP 시스템 테스트
HW-AI-Gateway 통신 시나리오 데모

이 스크립트는 다음을 테스트합니다:
1. HW → AI → Gateway (기기 제어)
2. AI → HW → AI → Gateway (추천 기반 제어)

실행 방법:
    PYTHONPATH=. python examples/test_mvp_system.py
"""
import asyncio
import httpx
import json
from datetime import datetime
import pytz

# 테스트 설정 (dotenv 사용)
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:8000")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:9000")

KST = pytz.timezone('Asia/Seoul')


class RealServerTester:
    """실제 서버 테스터"""
    
    def __init__(self):
        self.ai_server_url = AI_SERVER_URL
        self.gateway_url = GATEWAY_URL
        self.test_results = []
    
    async def test_ai_server_connection(self) -> bool:
        """AI 서버 연결 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ai_server_url}/health", timeout=10.0)
                if response.status_code == 200:
                    print(f"✅ AI 서버 연결 성공: {self.ai_server_url}")
                    return True
                else:
                    print(f"❌ AI 서버 응답 오류: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ AI 서버 연결 실패: {e}")
            return False
    
    async def test_gateway_connection(self) -> bool:
        """Gateway 서버 연결 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                # Gateway 헬스체크 (가정)
                response = await client.get(f"{self.gateway_url}/health", timeout=10.0)
                if response.status_code == 200:
                    print(f"✅ Gateway 서버 연결 성공: {self.gateway_url}")
                    return True
                else:
                    print(f"❌ Gateway 서버 응답 오류: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Gateway 서버 연결 실패: {e}")
            return False


async def test_direct_control():
    """시나리오 1: HW → AI → Gateway (직접 제어)"""
    print('\n' + '='*60)
    print('1️⃣  직접 제어 시나리오 (HW → AI → Gateway)')
    print('='*60)
    
    try:
        # AI 서버에 직접 제어 요청
        control_request = {
            "device_id": "b403_air_purifier_001",
            "action": "turn_on"
        }
        
        print(f"📱 HW → AI 제어 요청:")
        print(f"  - 기기: {control_request['device_id']}")
        print(f"  - 액션: {control_request['action']}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVER_URL}/api/lg/control",
                json=control_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI 서버 응답:")
                print(f"  - 메시지: {result['message']}")
                print(f"  - 기기: {result['device_id']}")
                print(f"  - 액션: {result['action']}")
                return True
            else:
                print(f"❌ AI 서버 오류: {response.status_code}")
                print(f"  응답: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 직접 제어 테스트 실패: {e}")
        return False


async def test_smart_recommendation():
    """시나리오 2: AI → HW → AI → Gateway (추천 기반 제어)"""
    print('\n' + '='*60)
    print('2️⃣  추천 기반 제어 시나리오 (AI → HW → AI → Gateway)')
    print('='*60)
    
    try:
        # AI 서버에 추천 요청
        recommendation_request = {
            "message": "에어컨 킬까요?"
        }
        
        print(f"🤖 AI → HW 추천 전송:")
        print(f"  - 추천 문구: \"{recommendation_request['message']}\"")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVER_URL}/api/recommendations/recommendations",
                json=recommendation_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI 서버 응답:")
                print(f"  - 메시지: {result['message']}")
                print(f"  - 사용자 확인: {result['confirm']}")
                
                if result['confirm'] == 'YES':
                    print(f"\n🎯 사용자가 허가했으므로 실제 제어 실행!")
                    print(f"  - AI → Gateway 제어 요청 전달됨")
                
                return True
            else:
                print(f"❌ AI 서버 오류: {response.status_code}")
                print(f"  응답: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 추천 기반 제어 테스트 실패: {e}")
        return False


async def test_multiple_scenarios():
    """다양한 시나리오 테스트"""
    print('\n' + '='*60)
    print('3️⃣  다양한 시나리오 테스트')
    print('='*60)
    
    scenarios = [
        {
            "name": "밤에 에어컨 켜기",
            "type": "direct",
            "request": {"device_id": "b403_ac_001", "action": "turn_on"}
        },
        {
            "name": "낮에 조명 끄기",
            "type": "direct", 
            "request": {"device_id": "b403_light_001", "action": "turn_off"}
        },
        {
            "name": "저녁에 TV 켜기 추천",
            "type": "recommendation",
            "request": {"message": "TV 켤까요?"}
        },
        {
            "name": "공기청정기 자동 모드",
            "type": "direct",
            "request": {"device_id": "b403_air_purifier_001", "action": "auto"}
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f'\n📋 시나리오 {i}: {scenario["name"]}')
        try:
            if scenario["type"] == "direct":
                # 직접 제어
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{AI_SERVER_URL}/api/lg/control",
                        json=scenario["request"]
                    )
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ 제어 성공: {result['message']}")
                        results.append(True)
                    else:
                        print(f"  ❌ 제어 실패: {response.status_code}")
                        results.append(False)
                        
            elif scenario["type"] == "recommendation":
                # 추천 기반 제어
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{AI_SERVER_URL}/api/recommendations/recommendations",
                        json=scenario["request"]
                    )
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ 추천 전송: {result['message']}")
                        print(f"  📝 사용자 응답: {result['confirm']}")
                        results.append(True)
                    else:
                        print(f"  ❌ 추천 실패: {response.status_code}")
                        results.append(False)
                        
        except Exception as e:
            print(f"  ❌ 시나리오 실패: {e}")
            results.append(False)
    
    return results


async def test_api_status():
    """API 상태 확인"""
    print('\n' + '='*60)
    print('4️⃣  API 상태 확인')
    print('='*60)
    
    endpoints = [
        ("AI 서버 루트", f"{AI_SERVER_URL}/"),
        ("AI 서버 헬스체크", f"{AI_SERVER_URL}/health"),
        ("LG 제어 상태", f"{AI_SERVER_URL}/api/lg/status"),
        ("추천 시스템 상태", f"{AI_SERVER_URL}/api/recommendations/status")
    ]
    
    for name, url in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {name}: {result.get('message', 'OK')}")
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")


async def main():
    """메인 테스트 실행"""
    print('\n' + '='*60)
    print('🚀 GazeHome AI MVP 시스템 테스트 (실제 서버)')
    print('='*60)
    print(f'⏰ 테스트 시작: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')
    print(f'🌐 AI 서버: {AI_SERVER_URL}')
    print(f'🌐 Gateway: {GATEWAY_URL}')
    
    results = []
    
    # 0. 서버 연결 테스트
    tester = RealServerTester()
    print('\n' + '='*60)
    print('0️⃣  서버 연결 테스트')
    print('='*60)
    
    ai_connected = await tester.test_ai_server_connection()
    gateway_connected = await tester.test_gateway_connection()
    
    if not ai_connected:
        print("❌ AI 서버 연결 실패로 테스트 중단")
        return
    
    # 1. API 상태 확인
    await test_api_status()
    
    # 2. 직접 제어 테스트
    results.append(await test_direct_control())
    
    # 3. 추천 기반 제어 테스트
    results.append(await test_smart_recommendation())
    
    # 4. 다양한 시나리오 테스트
    scenario_results = await test_multiple_scenarios()
    results.extend(scenario_results)
    
    # 최종 결과
    print('\n' + '='*60)
    print('📊 테스트 결과 요약')
    print('='*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print('\n🎉 모든 테스트 통과!')
        print('  ✅ HW → AI → Gateway (직접 제어)')
        print('  ✅ AI → HW → AI → Gateway (추천 기반 제어)')
        print('  ✅ 다양한 시나리오')
        print('\n🚀 MVP 시스템이 정상적으로 작동하고 있습니다!')
    else:
        print(f'\n⚠️  일부 테스트 실패 ({success_count}/{total_count})')
        print('위의 오류 메시지를 확인해주세요.')
    
    print(f'\n⏰ 테스트 완료: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')


if __name__ == '__main__':
    asyncio.run(main())
