"""
GazeHome AI Services - 데모 실행 스크립트
전체 시스템 데모를 실행하는 통합 스크립트

실행 방법:
    PYTHONPATH=. python examples/run_demo.py
"""
import asyncio
import subprocess
import time
import signal
import sys
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

class DemoRunner:
    """데모 실행 관리자"""
    
    def __init__(self):
        self.processes = []
        self.running = True
    
    def start_ai_server(self):
        """AI 서버 시작"""
        print("🤖 AI 서버 시작 중...")
        try:
            process = subprocess.Popen([
                "python", "main.py", "--mode", "gcp-dev"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(("AI Server", process))
            print("✅ AI 서버 시작 완료 (포트 8000)")
            return True
        except Exception as e:
            print(f"❌ AI 서버 시작 실패: {e}")
            return False
    
    def start_mock_servers(self):
        """Mock 서버들 시작"""
        print("🔧 Mock 서버들 시작 중...")
        try:
            process = subprocess.Popen([
                "python", "examples/mock_servers.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(("Mock Servers", process))
            print("✅ Mock 서버들 시작 완료 (포트 8080, 9000)")
            return True
        except Exception as e:
            print(f"❌ Mock 서버들 시작 실패: {e}")
            return False
    
    async def run_tests(self):
        """테스트 실행"""
        print("🧪 MVP 시스템 테스트 실행...")
        try:
            result = subprocess.run([
                "python", "examples/test_mvp_system.py"
            ], capture_output=True, text=True)
            
            print("📊 테스트 결과:")
            print(result.stdout)
            if result.stderr:
                print("⚠️ 오류 메시지:")
                print(result.stderr)
            
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 테스트 실행 실패: {e}")
            return False
    
    def cleanup(self):
        """프로세스 정리"""
        print("\n🧹 프로세스 정리 중...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 종료 완료")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {name} 강제 종료")
            except Exception as e:
                print(f"❌ {name} 종료 실패: {e}")
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"\n🛑 시그널 {signum} 수신, 데모 종료 중...")
        self.running = False
        self.cleanup()
        sys.exit(0)


async def main():
    """메인 데모 실행"""
    print('\n' + '='*60)
    print('🚀 GazeHome AI MVP 시스템 데모')
    print('='*60)
    print(f'⏰ 시작 시간: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}')
    
    runner = DemoRunner()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    try:
        # 1. AI 서버 시작
        if not runner.start_ai_server():
            print("❌ AI 서버 시작 실패로 데모 중단")
            return
        
        # 2. Mock 서버들 시작
        if not runner.start_mock_servers():
            print("❌ Mock 서버들 시작 실패로 데모 중단")
            runner.cleanup()
            return
        
        # 3. 서버들 시작 대기
        print("\n⏳ 서버들 시작 대기 중... (10초)")
        await asyncio.sleep(10)
        
        # 4. 테스트 실행
        print("\n" + "="*60)
        print("🧪 MVP 시스템 테스트 시작")
        print("="*60)
        
        test_success = await runner.run_tests()
        
        # 5. 결과 출력
        print("\n" + "="*60)
        print("📊 데모 결과")
        print("="*60)
        
        if test_success:
            print("🎉 데모 성공!")
            print("  ✅ AI 서버 정상 작동")
            print("  ✅ HW-AI-Gateway 통신 성공")
            print("  ✅ 다양한 시나리오 테스트 통과")
        else:
            print("⚠️ 데모 일부 실패")
            print("  위의 오류 메시지를 확인해주세요.")
        
        print(f"\n⏰ 완료 시간: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")}")
        
        # 6. 대기 (사용자가 결과를 확인할 수 있도록)
        print("\n🔄 데모 완료. 30초 후 자동 종료됩니다...")
        print("   (수동 종료: Ctrl+C)")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 데모 중단")
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")
    finally:
        runner.cleanup()
        print("\n👋 데모 종료")


if __name__ == "__main__":
    asyncio.run(main())
