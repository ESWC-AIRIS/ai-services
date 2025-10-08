"""
GazeHome AI Services - 기기 클릭 테스트 스크립트
하드웨어에서 전송할 클릭 이벤트를 테스트합니다.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


class GazeHomeClient:
    """GazeHome AI 서비스 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def check_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            response = requests.get(f"{self.api_url}/gaze/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_device_click(
        self,
        user_id: str,
        session_id: str,
        device_id: str,
        device_type: str,
        device_name: str,
        display_name: str,
        capabilities: list,
        current_state: dict,
        context: dict = None
    ) -> Dict[str, Any]:
        """기기 클릭 이벤트 전송"""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "clicked_device": {
                "device_id": device_id,
                "device_type": device_type,
                "device_name": device_name,
                "display_name": display_name,
                "capabilities": capabilities,
                "current_state": current_state
            },
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/gaze/click",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "response": response.text if 'response' in locals() else None}


def test_air_conditioner_click():
    """에어컨 클릭 테스트"""
    print("\n=== 테스트 1: 에어컨 클릭 (꺼진 상태) ===")
    
    client = GazeHomeClient()
    
    result = client.send_device_click(
        user_id="test_user_001",
        session_id="test_session_001",
        device_id="ac_living_room",
        device_type="air_conditioner",
        device_name="거실 에어컨",
        display_name="에어컨",
        capabilities=["on_off", "temperature", "mode", "fan_speed"],
        current_state={
            "is_on": False,
            "temperature": 24,
            "mode": "cool"
        },
        context={
            "location": "living_room",
            "outdoor_temperature": 32
        }
    )
    
    print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"\n추천 메시지: {rec.get('prompt_text')}")
        print(f"추천 명령어: {rec.get('action', {}).get('command')}")
        print(f"신뢰도: {rec.get('confidence')}")
    
    return result


def test_light_click():
    """조명 클릭 테스트"""
    print("\n=== 테스트 2: 조명 클릭 (켜진 상태) ===")
    
    client = GazeHomeClient()
    
    result = client.send_device_click(
        user_id="test_user_001",
        session_id="test_session_002",
        device_id="light_bedroom",
        device_type="light",
        device_name="침실 조명",
        display_name="조명",
        capabilities=["on_off", "brightness", "color"],
        current_state={
            "is_on": True,
            "brightness": 100,
            "color": "#FFFFFF"
        },
        context={
            "location": "bedroom",
            "time_of_day": "night"
        }
    )
    
    print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"\n추천 메시지: {rec.get('prompt_text')}")
        print(f"추천 명령어: {rec.get('action', {}).get('command')}")
        print(f"신뢰도: {rec.get('confidence')}")
    
    return result


def test_tv_click():
    """TV 클릭 테스트"""
    print("\n=== 테스트 3: TV 클릭 (꺼진 상태) ===")
    
    client = GazeHomeClient()
    
    result = client.send_device_click(
        user_id="test_user_002",
        session_id="test_session_003",
        device_id="tv_living_room",
        device_type="tv",
        device_name="거실 TV",
        display_name="TV",
        capabilities=["on_off", "volume", "channel"],
        current_state={
            "is_on": False,
            "volume": 15,
            "channel": 11
        },
        context={
            "location": "living_room",
            "time_of_day": "evening"
        }
    )
    
    print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"\n추천 메시지: {rec.get('prompt_text')}")
        print(f"추천 명령어: {rec.get('action', {}).get('command')}")
        print(f"신뢰도: {rec.get('confidence')}")
    
    return result


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("GazeHome AI Services - 기기 클릭 테스트")
    print("=" * 60)
    
    # 1. 시스템 상태 확인
    print("\n=== 시스템 상태 확인 ===")
    client = GazeHomeClient()
    status = client.check_status()
    print(f"상태: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    if "error" in status:
        print("\n⚠️ 서버가 실행 중이 아닙니다!")
        print("다음 명령어로 서버를 시작하세요:")
        print("  cd ai-services")
        print("  source .venv/Scripts/activate  # Windows")
        print("  source .venv/bin/activate       # macOS")
        print("  uvicorn app.main:app --reload")
        return
    
    # 2. 기기 클릭 테스트들
    try:
        test_air_conditioner_click()
        test_light_click()
        test_tv_click()
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
