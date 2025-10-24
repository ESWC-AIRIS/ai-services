"""
GazeHome AI Services - Recommendations Endpoints
AI → HW 추천 시스템 API 엔드포인트 (명세서에 맞춤)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import logging
import httpx
import google.generativeai as genai
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


# Gemini AI 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# 하드웨어 클라이언트 인스턴스
hardware_client = HardwareClient()

class AIRecommendationService:
    """AI 추천 서비스"""
    
    def __init__(self):
        self.model = model
    
    async def generate_smart_recommendation(self, context: str = None) -> Dict[str, Any]:
        """AI가 스마트 추천 생성 (제어 정보 포함)"""
        if not self.model:
            # Gemini API가 없으면 기본 추천 반환
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                "device_control": None
            }
        
        try:
            # 현재 시간 정보 추가
            from datetime import datetime
            import pytz
            KST = pytz.timezone('Asia/Seoul')
            now = datetime.now(KST)
            time_info = {
                "hour": now.hour,
                "day_of_week": now.strftime("%A"),
                "season": self._get_season(now.month)
            }
            
            # Gateway에서 등록된 기기 목록 및 상태 조회
            from app.api.endpoints.devices import gateway_client
            try:
                gateway_devices = await gateway_client.get_available_devices()
                available_devices = gateway_devices.get('response', [])
                
                # 각 기기의 상태도 함께 조회
                device_status_list = []
                for device in available_devices:
                    device_id = device['deviceId']
                    device_alias = device['deviceInfo']['alias']
                    device_type = device['deviceInfo']['deviceType']
                    
                    # 기기 상태 확인
                    device_status = await self._check_device_status(device_id)
                    status_text = "실행중" if device_status['is_running'] else "정지중"
                    control_text = "제어가능" if device_status['can_control'] else "제어불가"
                    
                    device_status_list.append(
                        f"- {device_alias} ({device_type}) - 상태: {status_text}, {control_text}"
                    )
                
                device_info_text = "\n".join(device_status_list) if device_status_list else "등록된 기기가 없습니다."
            except Exception as e:
                logger.warning(f"Gateway 기기 목록 조회 실패: {e}")
                device_info_text = "기기 정보를 확인할 수 없습니다."
            
            prompt = f"""
            당신은 스마트 홈 AI 어시스턴트입니다. 
            사용자의 현재 상황을 분석하여 적절한 기기 제어 추천을 해주세요.
            
            === 현재 상황 ===
            - 시간: {time_info['hour']}시 ({time_info['day_of_week']})
            - 계절: {time_info['season']}
            - 사용자 요청: {context or "일반적인 스마트 홈 환경"}
            
            === 등록된 기기 목록 ===
            {device_info_text}
            
            === 추천 가이드라인 ===
            1. 위에 나열된 등록된 기기 중에서만 추천하세요
            2. 기기 상태를 고려하여 추천하세요:
               - 이미 실행중인 기기는 끄기 추천
               - 정지중인 기기는 켜기 추천
               - 제어불가능한 기기는 추천하지 마세요
            3. 시간대별 적절한 추천 (아침: 조명, 저녁: 에어컨/공기청정기)
            4. 계절별 추천 (여름: 에어컨, 겨울: 난방, 봄/가을: 공기청정기)
            5. 사용자 요청에 맞는 구체적인 추천
            6. 친근하고 자연스러운 한국어 표현
            7. YES/NO로만 답변 가능하므로 "켜기/끄기" 같은 단순한 제어만 추천
            8. 온도 설정, 강도 조절, 모드 변경 등 복잡한 옵션 절대 제시 금지
            9. "에어컨 켤까요?", "조명 끌까요?" 같은 단순한 질문만 생성
            
            다음 JSON 형식으로 응답해주세요:
            {{
                "title": "에어컨 켤까요?",
                "contents": "현재 온도가 25도이므로 에어컨을 키시는 것을 추천드립니다.",
                "device_control": {{
                    "device_type": "air_conditioner",
                    "action": "turn_on"
                }}
            }}
            
            device_type 옵션: air_conditioner, air_purifier, dryer, washer, light
            action 옵션: turn_on, turn_off, clean, auto
            
            중요: 
            - 등록된 기기 목록에 있는 기기만 추천하세요
            - title은 5-10자 이내의 간단한 질문 형태
            - device_control은 반드시 포함
            - JSON 형식으로만 응답
            """
            
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # JSON 응답 파싱
            try:
                import json
                # JSON 부분만 추출 (```json ... ``` 형태일 수 있음)
                if '```json' in result:
                    json_start = result.find('```json') + 7
                    json_end = result.find('```', json_start)
                    json_str = result[json_start:json_end].strip()
                elif '{' in result and '}' in result:
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    json_str = result[json_start:json_end]
                else:
                    raise ValueError("JSON 형식을 찾을 수 없습니다")
                
                ai_response = json.loads(json_str)
                
                # AI가 생성한 구조화된 정보 사용
                title = ai_response.get('title', '스마트 홈 추천')
                contents = ai_response.get('contents', '현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.')
                device_control_info = ai_response.get('device_control', {})
                
                # 제어 정보가 있으면 Gateway에서 기기 찾기
                device_control = None
                if device_control_info:
                    device_control = await self._prepare_device_control_from_ai(device_control_info)
                
                return {
                    "title": title,
                    "contents": contents,
                    "device_control": device_control
                }
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error(f"AI JSON 응답 파싱 실패: {e}")
                # 파싱 실패 시 기본 추천 반환
                return {
                    "title": "스마트 홈 추천",
                    "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다.",
                    "device_control": None
                }
            
        except Exception as e:
            logger.error(f"AI 추천 생성 실패: {e}")
            return {
                "title": "스마트 홈 추천",
                "contents": "현재 상황에 맞는 스마트 홈 기기 제어를 추천드립니다."
            }
    
    def _get_season(self, month: int) -> str:
        """월에 따른 계절 반환"""
        if month in [12, 1, 2]:
            return "겨울"
        elif month in [3, 4, 5]:
            return "봄"
        elif month in [6, 7, 8]:
            return "여름"
        else:
            return "가을"
    
    async def _generate_title_from_content(self, contents: str) -> str:
        """AI가 내용을 보고 제목만 생성"""
        if not self.model:
            return "기기 제어할까요?"
        
        try:
            prompt = f"""
            다음 내용을 보고 간단한 제목(5-10자 이내)을 만들어주세요.
            
            내용: {contents}
            
            요구사항:
            - 5-10자 이내의 간단한 질문 형태
            - "~할까요?" 또는 "~할까요?" 형태
            - 복잡한 설명 없이 기기 제어만 언급
            - YES/NO로 답변 가능한 단순한 제어만
            
            예시:
            - "에어컨 켤까요?
            - "공기청정기 끌까요?"
            
            제목만 답변해주세요:
            """
            
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            
            # 제목이 너무 길면 기본값 반환
            if len(title) > 15:
                return "기기 제어할까요?"
            
            return title
            
        except Exception as e:
            logger.error(f"제목 생성 실패: {e}")
            return "기기 제어할까요?"
    
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
            
            # runState 확인
            run_state = property_info.get('runState', {})
            if run_state:
                current_state = run_state.get('currentState', {})
                if current_state:
                    state_values = current_state.get('value', {}).get('r', [])
                    if state_values:
                        status_info["current_state"] = state_values[0] if state_values else "UNKNOWN"
                        status_info["is_running"] = status_info["current_state"] in ["RUNNING", "COOLING", "HEATING"]
            
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
            
            # Gateway에서 사용 가능한 기기 목록 조회
            from app.api.endpoints.devices import gateway_client
            
            try:
                gateway_devices = await gateway_client.get_available_devices()
                available_devices = gateway_devices.get('response', [])
                
                # 적절한 기기 찾기
                target_device = find_matching_device(available_devices, device_type)
                
                if target_device:
                    device_id = target_device['deviceId']
                    device_alias = target_device['deviceInfo']['alias']
                    
                    # 기기 상태 확인
                    device_status = await self._check_device_status(device_id)
                    
                    # 상태 기반 스마트 액션 결정
                    smart_action = self._determine_smart_action(action, device_status)
                    
                    logger.info(f"✅ AI 제어 정보로 기기 찾기 완료: {device_alias} -> {smart_action}")
                    logger.info(f"🎯 기기 상태: {device_status['current_state']} (실행중: {device_status['is_running']})")
                    
                    return {
                        "device_id": device_id,
                        "device_type": device_type,
                        "action": smart_action,
                        "device_alias": device_alias,
                        "device_status": device_status
                    }
                else:
                    logger.warning(f"⚠️ AI가 요청한 기기 타입을 찾을 수 없습니다: {device_type}")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ AI 제어 정보로 기기 찾기 실패: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ AI 제어 정보 처리 중 오류 발생: {e}")
            return None
    
    def _determine_smart_action(self, original_action: str, device_status: Dict[str, Any]) -> str:
        """기기 상태에 따른 스마트 액션 결정"""
        current_state = device_status.get('current_state', 'UNKNOWN')
        is_running = device_status.get('is_running', False)
        
        # 이미 실행 중인 기기를 켜려고 하면 끄기로 변경
        if original_action == "turn_on" and is_running:
            logger.info(f"🔄 스마트 액션: 이미 실행 중이므로 끄기로 변경")
            return "turn_off"
        
        # 이미 꺼진 기기를 끄려고 하면 켜기로 변경
        if original_action == "turn_off" and not is_running:
            logger.info(f"🔄 스마트 액션: 이미 꺼져있으므로 켜기로 변경")
            return "turn_on"
        
        # 상태를 모르거나 제어 불가능한 경우 원래 액션 유지
        if not device_status.get('can_control', True):
            logger.warning(f"⚠️ 기기 제어 불가능: {device_status['device_id']}")
        
        return original_action

    async def _prepare_device_control(self, title: str, contents: str) -> Optional[Dict[str, Any]]:
        """추천 생성 시점에 제어 정보 미리 준비"""
        try:
            # 추천 내용에서 기기 제어 정보 추출
            device_info = extract_device_control_info(title, contents)
            
            if not device_info:
                logger.info("추천 내용에서 기기 제어 정보를 추출할 수 없습니다.")
                return None
            
            # Gateway에서 사용 가능한 기기 목록 조회
            from app.api.endpoints.devices import gateway_client
            
            try:
                gateway_devices = await gateway_client.get_available_devices()
                available_devices = gateway_devices.get('response', [])
                
                # 적절한 기기 찾기
                target_device = find_matching_device(available_devices, device_info['device_type'])
                
                if target_device:
                    logger.info(f"✅ 제어 정보 준비 완료: {target_device['deviceInfo']['alias']} -> {device_info['action']}")
                    return {
                        "device_id": target_device['deviceId'],
                        "device_type": device_info['device_type'],
                        "action": device_info['action'],
                        "device_alias": target_device['deviceInfo']['alias']
                    }
                else:
                    logger.warning(f"⚠️ 해당 기기 타입을 찾을 수 없습니다: {device_info['device_type']}")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ 제어 정보 준비 실패: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 제어 정보 준비 중 오류 발생: {e}")
            return None

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



