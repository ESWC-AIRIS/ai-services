"""
GazeHome AI Services - Demo Endpoints
데모 및 테스트용 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import pytz

from app.services.proactive_recommendation_service import get_proactive_service

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')

# 데모 시나리오 정의 (에어컨 & 공기청정기만)
DEMO_SCENARIOS = {
    "hot_weather_ac": {
        "name": "더운 날씨 냉방",
        "description": "기온 30도, 에어컨 냉방 모드 추천",
        "context": {
            "time_info": {
                "hour": 14,
                "time_period": "오후",
                "weekday": "Tuesday"
            },
            "weather": {
                "summary": "맑음, 30도, 매우 더움",
                "details": {"temperature": 30, "condition": "Clear", "humidity": 65}
            }
        },
        "device": {
            "device_id": "ac_living_room",
            "device_type": "air_conditioner",
            "device_name": "거실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "current_state": {"is_on": False, "temperature": 24, "mode": "cool"}
        }
    },
    "cold_weather_ac": {
        "name": "추운 날씨 난방",
        "description": "기온 5도, 에어컨 난방 모드 추천",
        "context": {
            "time_info": {
                "hour": 20,
                "time_period": "저녁",
                "weekday": "Friday"
            },
            "weather": {
                "summary": "흐림, 5도, 매우 추움",
                "details": {"temperature": 5, "condition": "Cloudy", "humidity": 50}
            }
        },
        "device": {
            "device_id": "ac_living_room",
            "device_type": "air_conditioner",
            "device_name": "거실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "current_state": {"is_on": False, "temperature": 22, "mode": "heat"}
        }
    },
    "rainy_dehumidifier": {
        "name": "비 오는 날 제습",
        "description": "비 오는 날, 습도 높을 때 에어컨 제습 모드 추천",
        "context": {
            "time_info": {
                "hour": 16,
                "time_period": "오후",
                "weekday": "Wednesday"
            },
            "weather": {
                "summary": "비, 22도, 습도 85%",
                "details": {"temperature": 22, "condition": "Rain", "humidity": 85}
            }
        },
        "device": {
            "device_id": "ac_living_room",
            "device_type": "air_conditioner",
            "device_name": "거실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "current_state": {"is_on": False, "temperature": 24, "mode": "dehumidify"}
        }
    },
    "dust_air_purifier": {
        "name": "미세먼지 공기청정기",
        "description": "미세먼지 나쁨, 공기청정기 강풍 모드 추천",
        "context": {
            "time_info": {
                "hour": 10,
                "time_period": "아침",
                "weekday": "Monday"
            },
            "weather": {
                "summary": "맑음, 20도, 미세먼지 나쁨",
                "details": {"temperature": 20, "condition": "Clear", "air_quality": "bad", "pm25": 80}
            }
        },
        "device": {
            "device_id": "air_purifier_living_room",
            "device_type": "air_purifier",
            "device_name": "거실 공기청정기",
            "display_name": "공기청정기",
            "capabilities": ["on_off", "fan_speed", "mode"],
            "current_state": {"is_on": False, "fan_speed": 1, "mode": "auto"}
        }
    },
    "night_air_purifier": {
        "name": "취침 시간 공기청정기",
        "description": "밤 11시, 공기청정기 수면 모드 추천",
        "context": {
            "time_info": {
                "hour": 23,
                "time_period": "밤",
                "weekday": "Sunday"
            },
            "weather": {
                "summary": "맑음, 18도",
                "details": {"temperature": 18, "condition": "Clear"}
            }
        },
        "device": {
            "device_id": "air_purifier_bedroom",
            "device_type": "air_purifier",
            "device_name": "침실 공기청정기",
            "display_name": "공기청정기",
            "capabilities": ["on_off", "fan_speed", "mode"],
            "current_state": {"is_on": False, "fan_speed": 1, "mode": "sleep"}
        }
    },
    "humid_weather": {
        "name": "습한 날씨 제습",
        "description": "습도 높은 날, 에어컨 제습 모드 추천",
        "context": {
            "time_info": {
                "hour": 15,
                "time_period": "오후",
                "weekday": "Thursday"
            },
            "weather": {
                "summary": "흐림, 25도, 습도 80%",
                "details": {"temperature": 25, "condition": "Cloudy", "humidity": 80}
            }
        },
        "device": {
            "device_id": "ac_bedroom",
            "device_type": "air_conditioner",
            "device_name": "침실 에어컨",
            "display_name": "에어컨",
            "capabilities": ["on_off", "temperature", "mode"],
            "current_state": {"is_on": False, "temperature": 24, "mode": "dehumidify"}
        }
    }
}


class DemoRequest(BaseModel):
    """데모 추천 생성 요청"""
    scenario: str = Field(..., description="시나리오 ID (예: evening_light, hot_weather_ac)")
    user_id: str = Field(default="demo_user", description="사용자 ID")


class DemoRecommendation(BaseModel):
    """데모 추천 응답"""
    scenario_name: str
    scenario_description: str
    context: Dict[str, Any]
    device: Dict[str, Any]
    recommendation: Optional[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(KST))


@router.get("/scenarios")
async def get_demo_scenarios():
    """
    사용 가능한 데모 시나리오 목록 조회
    
    Returns:
        시나리오 목록
    """
    scenarios = []
    for scenario_id, scenario_data in DEMO_SCENARIOS.items():
        scenarios.append({
            "id": scenario_id,
            "name": scenario_data["name"],
            "description": scenario_data["description"]
        })
    
    return {
        "status": "success",
        "count": len(scenarios),
        "scenarios": scenarios,
        "timestamp": datetime.now(KST).isoformat()
    }


@router.post("/recommendation", response_model=DemoRecommendation)
async def generate_demo_recommendation(request: DemoRequest):
    """
    데모 추천 생성
    
    선택한 시나리오에 따라 추천 메시지를 즉시 생성합니다.
    하드웨어 연동 없이 추천 메시지만 확인할 수 있습니다.
    
    Args:
        request: 데모 요청 (시나리오 ID)
        
    Returns:
        생성된 추천 메시지 및 상세 정보
    """
    try:
        # 시나리오 확인
        if request.scenario not in DEMO_SCENARIOS:
            raise HTTPException(
                status_code=400,
                detail=f"존재하지 않는 시나리오: {request.scenario}. "
                       f"사용 가능한 시나리오: {list(DEMO_SCENARIOS.keys())}"
            )
        
        scenario = DEMO_SCENARIOS[request.scenario]
        
        # ProactiveRecommendationService를 통해 추천 생성
        proactive_service = get_proactive_service()
        
        # LLM을 통한 추천 생성 (실제 로직 사용)
        recommendation = await proactive_service._generate_recommendation_with_llm(
            user_id=request.user_id,
            context=scenario["context"],
            available_devices=[scenario["device"]]
        )
        
        return DemoRecommendation(
            scenario_name=scenario["name"],
            scenario_description=scenario["description"],
            context=scenario["context"],
            device=scenario["device"],
            recommendation=recommendation,
            timestamp=datetime.now(KST)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"데모 추천 생성 실패: {str(e)}"
        )


@router.get("/recommendation/{scenario}")
async def get_demo_recommendation_by_path(scenario: str, user_id: str = "demo_user"):
    """
    데모 추천 생성 (GET 방식)
    
    브라우저에서 바로 테스트할 수 있도록 GET 방식도 지원합니다.
    
    Example:
        GET /api/demo/recommendation/evening_light
        GET /api/demo/recommendation/hot_weather_ac?user_id=test_user
    """
    request = DemoRequest(scenario=scenario, user_id=user_id)
    return await generate_demo_recommendation(request)


@router.get("/quick-test")
async def quick_demo_test():
    """
    빠른 데모 테스트
    
    모든 시나리오에 대한 추천을 한 번에 생성합니다.
    프레젠테이션이나 데모 시 유용합니다.
    """
    results = []
    
    for scenario_id, scenario_data in DEMO_SCENARIOS.items():
        try:
            proactive_service = get_proactive_service()
            
            recommendation = await proactive_service._generate_recommendation_with_llm(
                user_id="demo_user",
                context=scenario_data["context"],
                available_devices=[scenario_data["device"]]
            )
            
            results.append({
                "scenario_id": scenario_id,
                "scenario_name": scenario_data["name"],
                "status": "success",
                "prompt_text": recommendation.get("prompt_text") if recommendation else None,
                "should_recommend": recommendation.get("should_recommend") if recommendation else False
            })
        except Exception as e:
            results.append({
                "scenario_id": scenario_id,
                "scenario_name": scenario_data["name"],
                "status": "error",
                "error": str(e)
            })
    
    return {
        "status": "success",
        "total_scenarios": len(DEMO_SCENARIOS),
        "results": results,
        "timestamp": datetime.now(KST).isoformat()
    }

