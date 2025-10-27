"""
GazeHome AI Services - Recommendations Endpoints
AI → HW 추천 시스템 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
import httpx
# google.generativeai는 LangChain Agent로 대체되어 더 이상 사용하지 않음
from app.core.config import *
from app.models.recommendations import (
    RecommendationRequest, RecommendationResponse, 
    DeviceControlInfo, EnhancedRecommendation
)

router = APIRouter()
logger = logging.getLogger(__name__)


# 모델들은 app.models.recommendations에서 import


class HardwareClient:
    """하드웨어 통신 클라이언트"""
    
    def __init__(self, hardware_url: str = HARDWARE_URL):
        self.hardware_url = hardware_url
        self.recommendations_endpoint = HARDWARE_RECOMMENDATIONS_ENDPOINT
        self.timeout = 10.0
        logger.info(f"HardwareClient 초기화: url={self.hardware_url}")
    
    async def send_recommendation(self, title: str, contents: str) -> Dict[str, Any]:
        """하드웨어로 추천 전송"""
        try:
            payload = {
                "title": title,
                "contents": contents
            }
            
            logger.info(f"🚀 하드웨어로 추천 전송:")
            logger.info(f"  - 제목: \"{title}\"")
            logger.info(f"  - 내용: \"{contents}\"")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.recommendations_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    confirm = result.get('confirm', 'NO')
                    logger.info(f"✅ 하드웨어 응답 수신: {confirm}")
                    return result
                else:
                    logger.error(f"❌ 하드웨어 통신 실패: status={response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"하드웨어 통신 실패: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"하드웨어 통신 타임아웃: title={title}")
            raise HTTPException(status_code=504, detail="하드웨어 통신 타임아웃")
        except httpx.RequestError as e:
            logger.error(f"하드웨어 통신 에러: {e}")
            raise HTTPException(status_code=503, detail=f"하드웨어 통신 에러: {str(e)}")
        except Exception as e:
            logger.error(f"추천 전송 중 예외 발생: {e}")
            raise HTTPException(status_code=500, detail=f"추천 전송 실패: {str(e)}")


# 추천 Agent 설정
from app.agents.recommendation_agent import create_agent
recommendation_agent = create_agent()

# 하드웨어 클라이언트 인스턴스
hardware_client = HardwareClient()

class AIRecommendationService:
    """AI 추천 서비스 (추천 Agent 사용)"""
    
    def __init__(self):
        self.agent = recommendation_agent
    
    async def generate_smart_recommendation(self, context: str = None) -> Dict[str, Any]:
        """추천 Agent가 스마트 추천 생성 (제어 정보 포함)"""
        try:
            # 추천 Agent로 추천 생성
            recommendation = await self.agent.generate_recommendation(context)
            
            # recommendation이 None이거나 유효하지 않은 경우 처리
            if not recommendation or not isinstance(recommendation, dict):
                logger.warning("추천 Agent가 유효하지 않은 응답을 반환했습니다.")
                return {
                    "title": "스마트 홈 추천",
                    "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                    "device_control": None
                }
            
            # Agent가 이미 Gateway API를 호출했으므로 중복 호출 제거
            # 제어 정보가 있으면 Gateway에서 기기 찾기
            device_control = None
            if recommendation.get('device_control'):
                device_control_info = recommendation['device_control']
                device_control = await self._prepare_device_control_from_ai(device_control_info)
            
            return {
                "title": recommendation.get('title', '스마트 홈 추천'),
                "contents": recommendation.get('contents', '현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.'),
                "device_control": device_control
            }
            
        except Exception as e:
            logger.error(f"추천 Agent 추천 생성 실패: {e}")
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                "device_control": None
            }
    
    # _get_season 메서드는 추천 Agent로 대체되어 제거됨
    # 추천 Agent가 MCP Weather를 통해 실시간 날씨 정보를 받아오므로 하드코딩된 계절 정보 불필요
    
    # _generate_title_from_content 메서드는 추천 Agent로 대체되어 제거됨
    # 추천 Agent에서 title과 contents를 함께 생성하므로 별도 제목 생성이 불필요
    
    async def _check_device_status(self, device_id: str) -> Dict[str, Any]:
        """기기 상태 확인"""
        try:
            from app.api.endpoints.devices import gateway_client
            
            device_profile = await gateway_client.get_device_profile(device_id)
            response = device_profile.get('response', {})
            property_info = response.get('property', {})
            
            # 기기 상태 정보 추출
            status_info = {
                "device_id": device_id,
                "is_online": True,  # Gateway에서 응답이 오면 온라인
                "current_state": "UNKNOWN",
                "is_running": False,
                "can_control": True
            }
            
            # runState 확인 (Gateway에서 실제 값이 제공되지 않으므로 기본값 사용)
            run_state = property_info.get('runState', {})
            if run_state:
                current_state = run_state.get('currentState', {})
                if current_state:
                    state_values = current_state.get('value', {}).get('r', [])
                    if state_values:
                        status_info["current_state"] = state_values[0] if state_values else "UNKNOWN"
                        status_info["is_running"] = status_info["current_state"] in ["RUNNING", "COOLING", "HEATING"]
                    else:
                        # Gateway에서 실제 상태 값을 제공하지 않으므로 기본값 사용
                        status_info["current_state"] = "UNKNOWN"
                        status_info["is_running"] = False
                        logger.warning(f"⚠️ Gateway에서 기기 상태 값을 제공하지 않음: {device_id}")
            
            # remoteControlEnable 확인
            remote_control = property_info.get('remoteControlEnable', {})
            if remote_control:
                control_enabled = remote_control.get('remoteControlEnabled', {})
                if control_enabled:
                    control_values = control_enabled.get('value', {}).get('r', [])
                    if control_values:
                        status_info["can_control"] = control_values[0] if control_values else False
            
            logger.info(f"🔍 기기 상태 확인: {device_id} -> {status_info['current_state']} (실행중: {status_info['is_running']})")
            return status_info
            
        except Exception as e:
            logger.error(f"❌ 기기 상태 확인 실패: {device_id} - {e}")
            return {
                "device_id": device_id,
                "is_online": False,
                "current_state": "UNKNOWN",
                "is_running": False,
                "can_control": False
            }
    
    async def _prepare_device_control_from_ai(self, device_control_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """AI가 생성한 제어 정보로 기기 찾기 (상태 확인 포함)"""
        try:
            device_type = device_control_info.get('device_type')
            action = device_control_info.get('action')
            
            if not device_type or not action:
                logger.warning("AI가 생성한 제어 정보가 불완전합니다.")
                return None
            
            # Agent가 이미 Gateway API를 호출하고 적절한 기기를 선택했으므로
            # 단순히 Agent 결과를 그대로 사용 (추가 Gateway API 호출 없음)
            try:
                # Agent가 이미 기기 정보를 처리했으므로 기본 제어 정보만 반환
                logger.info(f"✅ Agent가 선택한 기기 제어: {device_type} -> {action}")
                
                return {
                    "device_type": device_type,
                    "action": action,
                    "source": "agent_recommendation"
                }
                    
            except Exception as e:
                logger.error(f"기기 제어 정보 준비 실패: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ AI 제어 정보 처리 중 오류 발생: {e}")
            return None
    
    # _determine_smart_action 메서드는 추천 Agent로 대체되어 제거됨
    # 추천 Agent가 기기 상태를 고려한 스마트 액션을 직접 결정하므로 불필요
    
    # _prepare_device_control 메서드는 추천 Agent로 대체되어 제거됨
    # 추천 Agent에서 device_control 정보를 직접 생성하므로 이 메서드는 더 이상 필요하지 않음

# AI 추천 서비스 인스턴스
ai_service = AIRecommendationService()


async def execute_saved_control(device_control: Optional[Dict[str, Any]]):
    """저장된 제어 정보로 바로 실행"""
    try:
        if not device_control:
            logger.info("ℹ️ 제어 정보가 없습니다.")
            return
        
        logger.info(f"🎯 저장된 제어 실행: {device_control['device_alias']} -> {device_control['action']}")
        
        # Gateway를 통해 실제 기기 제어
        from app.api.endpoints.devices import gateway_client
        
        control_result = await gateway_client.control_device(
            device_id=device_control['device_id'],
            action=device_control['action']
        )
        
        logger.info(f"✅ 기기 제어 완료: {device_control['device_alias']} -> {device_control['action']}")
        logger.info(f"   제어 결과: {control_result.get('message', '성공')}")
        
    except Exception as e:
        logger.error(f"❌ 저장된 제어 실행 실패: {e}")


# extract_device_control_info 함수 제거됨
# 이제 AI가 직접 구조화된 정보를 생성하므로 불필요


def find_matching_device(available_devices: List[Dict], target_device_type: str) -> Optional[Dict]:
    """사용 가능한 기기 목록에서 타겟 기기 타입과 일치하는 기기 찾기 (추천 생성 시점에만 사용)"""
    try:
        # 기기 타입 매핑
        device_type_mappings = {
            'air_conditioner': ['DEVICE_AIR_CONDITIONER'],
            'air_purifier': ['DEVICE_AIR_PURIFIER'],
            'dryer': ['DEVICE_DRYER'],
            'washer': ['DEVICE_WASHER']
        }
        
        target_types = device_type_mappings.get(target_device_type, [])
        
        for device in available_devices:
            device_info = device.get('deviceInfo', {})
            device_type = device_info.get('deviceType', '')
            
            if device_type in target_types:
                return device
        
        return None
        
    except Exception as e:
        logger.error(f"기기 매칭 실패: {e}")
        return None


@router.post("/", response_model=RecommendationResponse)
async def send_smart_recommendation(request: RecommendationRequest):
    """
    AI → HW: 추천 문구 전달 (유저 컨펌용) (명세서)
    
    AI가 유저별 맞춤형 추천을 생성하여 하드웨어(유저)에게 허가를 요청합니다.
    """
    try:
        logger.info(f"🤖 AI → HW 추천 전송:")
        logger.info(f"  - 제목: \"{request.title}\"")
        logger.info(f"  - 내용: \"{request.contents}\"")
        
        # AI 기반 스마트 추천 개선
        enhanced_recommendation = await ai_service.generate_smart_recommendation(
            context=f"사용자 요청: {request.title} - {request.contents}"
        )
        
        logger.info(f"🧠 AI 추천 개선:")
        logger.info(f"  - AI 제목: \"{enhanced_recommendation['title']}\"")
        logger.info(f"  - AI 내용: \"{enhanced_recommendation['contents']}\"")
        
        # 하드웨어로 개선된 추천 전송
        hardware_response = await hardware_client.send_recommendation(
            title=enhanced_recommendation['title'],
            contents=enhanced_recommendation['contents']
        )
        
        # 응답 검증
        confirm = hardware_response.get('confirm', 'NO')
        if confirm not in ['YES', 'NO']:
            confirm = 'NO'  # 기본값
        
        # 사용자가 YES로 답한 경우 실제 기기 제어 실행
        if confirm == 'YES':
            logger.info("✅ 사용자가 추천을 승인했습니다. 기기 제어를 실행합니다.")
            await execute_saved_control(enhanced_recommendation.get('device_control'))
        
        # device_control 정보를 DeviceControlInfo 객체로 변환
        device_control_info = None
        if enhanced_recommendation.get('device_control'):
            control_data = enhanced_recommendation['device_control']
            device_control_info = DeviceControlInfo(
                device_id=control_data.get('device_id', ''),
                device_type=control_data.get('device_type', ''),
                action=control_data.get('action', ''),
                device_alias=control_data.get('device_alias', '')
            )
        
        return RecommendationResponse(
            message=f"AI 추천: {enhanced_recommendation['title']} - {enhanced_recommendation['contents']}",
            confirm=confirm,
            device_control=device_control_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"추천 전송 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"추천 전송 실패: {str(e)}"
        )



