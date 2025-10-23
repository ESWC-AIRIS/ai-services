"""
GazeHome AI Services - 기존 API 테스트
실제 서버의 기존 API를 사용한 테스트

실행 방법:
    PYTHONPATH=. python examples/test_existing_api.py
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

AI_SERVER_URL = os.getenv("AI_SERVER_URL")
GATEWAY_URL = os.getenv("GATEWAY_URL")

KST = pytz.timezone('Asia/Seoul')


async def test_existing_apis():
    """기존 API 테스트"""
    print('\n' + '='*60)
    print('🚀 GazeHome AI 기존 API 테스트')
    print('='*60)
    print(f'⏰ 테스트 시작: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')
    print(f'🌐 AI 서버: {AI_SERVER_URL}')
    print(f'🌐 Gateway: {GATEWAY_URL}')
    
    results = []
    
    # 1. 서버 연결 테스트
    print('\n' + '='*60)
    print('1️⃣  서버 연결 테스트')
    print('='*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVER_URL}/health", timeout=10.0)
            if response.status_code == 200:
                print(f"✅ AI 서버 연결 성공")
                results.append(True)
            else:
                print(f"❌ AI 서버 연결 실패: {response.status_code}")
                results.append(False)
    except Exception as e:
        print(f"❌ AI 서버 연결 실패: {e}")
        results.append(False)
    
    # 2. 기기 제어 테스트 (기존 API 사용)
    print('\n' + '='*60)
    print('2️⃣  기기 제어 테스트 (기존 API)')
    print('='*60)
    
    try:
        # 기존 /api/devices/control API 사용
        control_request = {
            "device_id": "b403_air_purifier_001",
            "action": "turn_on",
            "user_id": "test_user"
        }
        
        print(f"📱 기기 제어 요청:")
        print(f"  - 기기: {control_request['device_id']}")
        print(f"  - 액션: {control_request['action']}")
        print(f"  - 사용자: {control_request['user_id']}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVER_URL}/api/devices/control",
                json=control_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 기기 제어 성공:")
                print(f"  - 응답: {result}")
                results.append(True)
            else:
                print(f"❌ 기기 제어 실패: {response.status_code}")
                print(f"  응답: {response.text}")
                results.append(False)
                
    except Exception as e:
        print(f"❌ 기기 제어 테스트 실패: {e}")
        results.append(False)
    
    # 3. 시선 클릭 테스트 (기존 API 사용)
    print('\n' + '='*60)
    print('3️⃣  시선 클릭 테스트 (기존 API)')
    print('='*60)
    
    try:
        # 기존 /api/gaze/click API 사용
        gaze_request = {
            "user_id": "test_user",
            "session_id": "test_session_001",
            "clicked_device": {
                "device_id": "b403_ac_001",
                "device_type": "air_conditioner",
                "device_name": "거실 에어컨",
                "display_name": "에어컨",
                "capabilities": ["on_off", "temperature", "fan_speed"],
                "current_state": {
                    "is_on": False,
                    "temperature": 24,
                    "fan_speed": "auto"
                }
            },
            "context": {
                "room": "거실",
                "time": "23:50"
            }
        }
        
        print(f"👁️ 시선 클릭 요청:")
        print(f"  - 사용자: {gaze_request['user_id']}")
        print(f"  - 클릭된 기기: {gaze_request['clicked_device']['display_name']}")
        print(f"  - 기기 상태: {gaze_request['clicked_device']['current_state']}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVER_URL}/api/gaze/click",
                json=gaze_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 시선 클릭 처리 성공:")
                print(f"  - 상태: {result.get('status')}")
                print(f"  - 메시지: {result.get('message')}")
                if result.get('recommendation'):
                    print(f"  - 추천: {result.get('recommendation')}")
                results.append(True)
            else:
                print(f"❌ 시선 클릭 처리 실패: {response.status_code}")
                print(f"  응답: {response.text}")
                results.append(False)
                
    except Exception as e:
        print(f"❌ 시선 클릭 테스트 실패: {e}")
        results.append(False)
    
    # 4. 컨텍스트 분석 테스트
    print('\n' + '='*60)
    print('4️⃣  컨텍스트 분석 테스트')
    print('='*60)
    
    try:
        context_request = {
            "user_id": "test_user",
            "location": "거실",
            "time_of_day": "저녁",
            "weather": {
                "temperature": 25,
                "humidity": 60,
                "description": "맑음"
            },
            "device_states": {
                "air_conditioner": {"is_on": False, "temperature": 24},
                "light": {"is_on": True, "brightness": 80}
            }
        }
        
        print(f"🧠 컨텍스트 분석 요청:")
        print(f"  - 사용자: {context_request['user_id']}")
        print(f"  - 위치: {context_request['location']}")
        print(f"  - 시간: {context_request['time_of_day']}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVER_URL}/api/context/analyze",
                json=context_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 컨텍스트 분석 성공:")
                print(f"  - 분석 결과: {result}")
                results.append(True)
            else:
                print(f"❌ 컨텍스트 분석 실패: {response.status_code}")
                print(f"  응답: {response.text}")
                results.append(False)
                
    except Exception as e:
        print(f"❌ 컨텍스트 분석 테스트 실패: {e}")
        results.append(False)
    
    # 5. 기기 목록 조회 테스트
    print('\n' + '='*60)
    print('5️⃣  기기 목록 조회 테스트')
    print('='*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AI_SERVER_URL}/api/devices/",
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 기기 목록 조회 성공:")
                print(f"  - 등록된 기기 수: {len(result) if isinstance(result, list) else 'N/A'}")
                print(f"  - 기기 목록: {result}")
                results.append(True)
            else:
                print(f"❌ 기기 목록 조회 실패: {response.status_code}")
                print(f"  응답: {response.text}")
                results.append(False)
                
    except Exception as e:
        print(f"❌ 기기 목록 조회 테스트 실패: {e}")
        results.append(False)
    
    # 최종 결과
    print('\n' + '='*60)
    print('📊 테스트 결과 요약')
    print('='*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print('\n🎉 모든 테스트 통과!')
        print('  ✅ 서버 연결')
        print('  ✅ 기기 제어')
        print('  ✅ 시선 클릭 처리')
        print('  ✅ 컨텍스트 분석')
        print('  ✅ 기기 목록 조회')
        print('\n🚀 기존 API 시스템이 정상적으로 작동하고 있습니다!')
    else:
        print(f'\n⚠️  일부 테스트 실패 ({success_count}/{total_count})')
        print('위의 오류 메시지를 확인해주세요.')
    
    print(f'\n⏰ 테스트 완료: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')


if __name__ == '__main__':
    asyncio.run(test_existing_apis())
