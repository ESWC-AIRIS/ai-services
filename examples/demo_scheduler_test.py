"""
GazeHome AI Services - 데모용 스케줄러 테스트
스케줄러 30분 대기 없이 즉시 테스트할 수 있는 데모 스크립트
"""

import asyncio
import httpx
import json
from datetime import datetime
import pytz

# AI 서버 설정
AI_SERVER_URL = "http://localhost:8000"

class DemoSchedulerTest:
    """데모용 스케줄러 테스트 클래스"""
    
    def __init__(self):
        self.ai_server_url = AI_SERVER_URL
    
    async def test_scheduler_immediately(self):
        """스케줄러를 즉시 실행 (30분 대기 없이)"""
        print("🚀 데모용 스케줄러 테스트 시작")
        print("=" * 50)
        
        try:
            # 스케줄러 테스트 엔드포인트 호출
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.ai_server_url}/api/scheduler/test")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ 스케줄러 테스트 성공!")
                    print(f"📅 시간: {result.get('timestamp')}")
                    print(f"🤖 추천 여부: {result.get('should_recommend')}")
                    
                    if result.get('should_recommend'):
                        print(f"📝 제목: {result.get('title')}")
                        print(f"📄 내용: {result.get('contents')}")
                        if result.get('device_control'):
                            device_info = result['device_control']
                            print(f"🎯 제어 정보: {device_info.get('device_alias')} -> {device_info.get('action')}")
                    else:
                        print(f"❌ 추천 조건 미충족: {result.get('reason')}")
                else:
                    print(f"❌ 스케줄러 테스트 실패: {response.status_code}")
                    print(f"오류: {response.text}")
                    
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
    
    async def test_scheduler_start(self):
        """스케줄러 시작"""
        print("\n🔄 스케줄러 시작 테스트")
        print("-" * 30)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_server_url}/api/scheduler/start",
                    json={"user_id": "demo_user", "interval_minutes": 1}  # 1분 간격으로 설정
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 스케줄러 시작: {result.get('message')}")
                else:
                    print(f"❌ 스케줄러 시작 실패: {response.text}")
                    
        except Exception as e:
            print(f"❌ 스케줄러 시작 중 오류: {e}")
    
    async def test_scheduler_status(self):
        """스케줄러 상태 확인"""
        print("\n📊 스케줄러 상태 확인")
        print("-" * 30)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ai_server_url}/api/scheduler/status")
                
                if response.status_code == 200:
                    status = response.json()
                    print(f"🔄 실행 상태: {status.get('is_running')}")
                    print(f"👤 사용자: {status.get('user_id')}")
                    print(f"⏰ 간격: {status.get('interval_minutes')}분")
                    print(f"🕐 마지막 확인: {status.get('last_check')}")
                else:
                    print(f"❌ 상태 확인 실패: {response.text}")
                    
        except Exception as e:
            print(f"❌ 상태 확인 중 오류: {e}")

async def main():
    """메인 데모 함수"""
    demo = DemoSchedulerTest()
    
    print("🎯 GazeHome AI Services - 스케줄러 데모")
    print("=" * 50)
    
    # 1. 스케줄러 즉시 테스트
    await demo.test_scheduler_immediately()
    
    # 2. 스케줄러 시작
    await demo.test_scheduler_start()
    
    # 3. 스케줄러 상태 확인
    await demo.test_scheduler_status()
    
    print("\n🎉 데모 완료!")
    print("💡 팁: 스케줄러가 시작되면 1분마다 자동으로 추천을 생성합니다.")

if __name__ == "__main__":
    asyncio.run(main())
