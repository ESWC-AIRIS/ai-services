"""
GazeHome AI 서비스 전체 시스템 테스트

이 스크립트는 다음을 테스트합니다:
1. MCP Weather API (실시간 날씨 데이터)
2. Gemini LLM (의도 추론 및 추천)
3. 전체 추천 시스템 통합

실행 방법:
    PYTHONPATH=. python examples/test_full_system.py
"""
import asyncio
from app.mcp import mcp_client
from app.services.llm_service import LLMService


async def test_weather_mcp():
    """날씨 MCP 테스트"""
    print('\n' + '='*60)
    print('1️⃣  날씨 MCP 테스트')
    print('='*60)
    
    try:
        # 날씨 정보 조회
        weather = await mcp_client.get_weather()
        print(f'\n📍 현재 날씨:')
        print(f'  - 위치: {weather.get("location")}, {weather.get("country")}')
        print(f'  - 온도: {weather.get("temperature")}℃')
        print(f'  - 체감온도: {weather.get("feels_like")}℃')
        print(f'  - 날씨: {weather.get("description")} ({weather.get("main")})')
        print(f'  - 습도: {weather.get("humidity")}%')
        print(f'  - 풍속: {weather.get("wind_speed")}m/s')
        
        # 날씨 요약
        summary = await mcp_client.get_weather_summary()
        print(f'\n📝 날씨 요약: {summary}')
        
        # 데이터 출처 확인
        source = weather.get('source')
        if source == 'openweathermap':
            print('\n✅ 실제 OpenWeatherMap API 연동 성공!')
        else:
            print('\n⚠️  Mock 데이터 사용 중 (API 키 확인 필요)')
        
        return True
        
    except Exception as e:
        print(f'\n❌ 날씨 MCP 테스트 실패: {e}')
        return False


async def test_llm_recommendation():
    """LLM 추천 시스템 테스트"""
    print('\n' + '='*60)
    print('2️⃣  LLM 추천 시스템 테스트')
    print('='*60)
    
    try:
        llm = LLMService()
        print('\n✅ LLM 서비스 초기화 완료')
        
        # 테스트 시나리오 1: 밤에 에어컨 클릭 (꺼진 상태)
        print('\n📋 테스트 시나리오 1: 밤에 에어컨 클릭')
        device_info = {
            'device_id': 'ac_001',
            'device_type': 'air_conditioner',
            'device_name': '거실 에어컨',
            'display_name': '에어컨',
            'capabilities': ['on_off', 'temperature', 'fan_speed'],
            'current_state': {
                'is_on': False,
                'temperature': 24,
                'fan_speed': 'auto'
            }
        }
        
        context = {
            'user_id': 'test_user',
            'session_id': 'test_session',
            'room': '거실',
            'time': '23:50'
        }
        
        print(f'  - 시간: {context["time"]} (밤)')
        print(f'  - 기기: {device_info["device_name"]}')
        print(f'  - 현재 상태: 꺼짐')
        
        print('\n🔄 추천 생성 중...')
        result = await llm.generate_device_recommendation(device_info, context)
        
        print('\n✅ 추천 생성 완료!')
        print('-' * 60)
        print(f'🎯 의도: {result["intent"]}')
        print(f'📊 신뢰도: {result["confidence"]}')
        print(f'💬 안내 메시지: {result["prompt_text"]}')
        print(f'\n🎬 추천 액션:')
        print(f'  - 기기: {result["action"]["device_id"]}')
        print(f'  - 명령: {result["action"]["command"]}')
        print(f'  - 파라미터: {result["action"]["parameters"]}')
        print(f'\n💡 추론 근거:')
        print(f'  {result["reasoning"]}')
        print('-' * 60)
        
        return True
        
    except Exception as e:
        print(f'\n❌ LLM 추천 테스트 실패: {e}')
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_scenarios():
    """다양한 시나리오 테스트"""
    print('\n' + '='*60)
    print('3️⃣  다양한 시나리오 테스트')
    print('='*60)
    
    llm = LLMService()
    
    scenarios = [
        {
            'name': '낮에 조명 클릭 (켜진 상태)',
            'device': {
                'device_id': 'light_001',
                'device_type': 'light',
                'device_name': '거실 조명',
                'display_name': '조명',
                'capabilities': ['on_off', 'brightness'],
                'current_state': {'is_on': True, 'brightness': 80}
            },
            'context': {'user_id': 'test', 'session_id': 'test', 'time': '14:30'}
        },
        {
            'name': '저녁에 TV 클릭 (꺼진 상태)',
            'device': {
                'device_id': 'tv_001',
                'device_type': 'tv',
                'device_name': '거실 TV',
                'display_name': 'TV',
                'capabilities': ['on_off', 'channel', 'volume'],
                'current_state': {'is_on': False, 'channel': 11, 'volume': 20}
            },
            'context': {'user_id': 'test', 'session_id': 'test', 'time': '19:00'}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f'\n📋 시나리오 {i}: {scenario["name"]}')
        try:
            result = await llm.generate_device_recommendation(
                scenario['device'], 
                scenario['context']
            )
            print(f'  ✅ 의도: {result["intent"]}')
            print(f'  💬 안내: {result["prompt_text"]}')
        except Exception as e:
            print(f'  ❌ 실패: {e}')


async def main():
    """메인 테스트 실행"""
    print('\n' + '='*60)
    print('🚀 GazeHome AI 서비스 전체 시스템 테스트')
    print('='*60)
    
    results = []
    
    # 1. 날씨 MCP 테스트
    results.append(await test_weather_mcp())
    
    # 2. LLM 추천 시스템 테스트
    results.append(await test_llm_recommendation())
    
    # 3. 다양한 시나리오 테스트
    await test_multiple_scenarios()
    
    # 최종 결과
    print('\n' + '='*60)
    print('📊 테스트 결과 요약')
    print('='*60)
    
    if all(results):
        print('\n🎉 모든 테스트 통과!')
        print('  ✅ MCP Weather API')
        print('  ✅ Gemini LLM')
        print('  ✅ 추천 생성 시스템')
        print('\n시스템이 정상적으로 작동하고 있습니다! 🚀')
    else:
        print('\n⚠️  일부 테스트 실패')
        print('위의 오류 메시지를 확인해주세요.')


if __name__ == '__main__':
    asyncio.run(main())
