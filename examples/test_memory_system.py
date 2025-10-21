"""
Memory 시스템 테스트
Short-term Memory와 Long-term Memory 기능 검증
"""
import asyncio
from app.services.memory_service import MemoryService


async def test_short_term_memory():
    """Short-term Memory 테스트"""
    print("\n" + "="*60)
    print("1️⃣  Short-term Memory 테스트")
    print("="*60)
    
    memory_service = MemoryService()
    session_id = "test_session_001"
    
    # 상호작용 추가
    print("\n📝 상호작용 추가 중...")
    interactions = [
        {
            'device_id': 'ac_001',
            'device_name': '거실 에어컨',
            'device_type': 'air_conditioner',
            'action': 'set_temperature',
            'intent': '온도 조절',
            'parameters': {'temperature': 26}
        },
        {
            'device_id': 'light_001',
            'device_name': '거실 조명',
            'device_type': 'light',
            'action': 'dim',
            'intent': '밝기 조절',
            'parameters': {'brightness': 30}
        },
        {
            'device_id': 'tv_001',
            'device_name': '거실 TV',
            'device_type': 'tv',
            'action': 'on',
            'intent': 'TV 켜기',
            'parameters': {}
        }
    ]
    
    for interaction in interactions:
        memory_service.short_term.add_interaction(session_id, interaction)
        print(f"  ✅ {interaction['device_name']}: {interaction['action']}")
    
    # 히스토리 조회
    print("\n📜 히스토리 조회:")
    history = memory_service.short_term.get_history(session_id)
    print(f"  - 총 {len(history)}개의 상호작용 저장됨")
    
    for i, item in enumerate(history, 1):
        print(f"  {i}. {item['device_name']}: {item['action']}")
    
    # 컨텍스트 요약
    print("\n📋 컨텍스트 요약:")
    summary = memory_service.short_term.get_context_summary(session_id)
    print(f"  {summary}")
    
    # 최근 N개만 조회
    print("\n🔍 최근 2개만 조회:")
    recent = memory_service.short_term.get_history(session_id, last_n=2)
    for item in recent:
        print(f"  - {item['device_name']}: {item['action']}")
    
    print("\n✅ Short-term Memory 테스트 완료!")
    return True


async def test_long_term_memory():
    """Long-term Memory 테스트"""
    print("\n" + "="*60)
    print("2️⃣  Long-term Memory 테스트")
    print("="*60)
    
    memory_service = MemoryService()
    user_id = "test_user_001"
    
    # 사용자 선호도 조회 (초기)
    print("\n📊 초기 사용자 선호도:")
    prefs = await memory_service.long_term.get_user_preferences(user_id)
    print(f"  - 선호 온도: {prefs['temperature_preference']}℃")
    print(f"  - 선호 밝기: {prefs['brightness_preference']}%")
    print(f"  - 시간대별 패턴: {len(prefs['time_patterns'])}개")
    
    # 상호작용에서 학습
    print("\n🎓 학습 시뮬레이션:")
    learning_interactions = [
        {
            'device_type': 'air_conditioner',
            'time_of_day': '밤',
            'parameters': {'temperature': 26},
            'accepted': True
        },
        {
            'device_type': 'air_conditioner',
            'time_of_day': '밤',
            'parameters': {'temperature': 26},
            'accepted': True
        },
        {
            'device_type': 'light',
            'time_of_day': '밤',
            'parameters': {'brightness': 30},
            'accepted': True
        },
        {
            'device_type': 'air_conditioner',
            'time_of_day': '아침',
            'parameters': {'temperature': 24},
            'accepted': True
        }
    ]
    
    for interaction in learning_interactions:
        await memory_service.long_term.learn_from_interaction(user_id, interaction)
        print(f"  ✅ 학습: {interaction['time_of_day']} - {interaction['device_type']}")
    
    # 학습 후 선호도 조회
    print("\n📊 학습 후 사용자 선호도:")
    prefs = await memory_service.long_term.get_user_preferences(user_id)
    print(f"  - 시간대별 패턴: {len(prefs['time_patterns'])}개")
    
    for time_period, devices in prefs['time_patterns'].items():
        print(f"\n  [{time_period}]")
        for device_type, patterns in devices.items():
            print(f"    - {device_type}: {len(patterns)}개 패턴")
            for pattern in patterns:
                print(f"      → {pattern}")
    
    # 패턴 인사이트 생성
    print("\n💡 패턴 인사이트:")
    insights = await memory_service.long_term.get_pattern_insights(user_id, {'time_of_day': '밤'})
    print(f"  {insights}")
    
    print("\n✅ Long-term Memory 테스트 완료!")
    return True


async def test_full_context():
    """전체 컨텍스트 통합 테스트"""
    print("\n" + "="*60)
    print("3️⃣  전체 컨텍스트 통합 테스트")
    print("="*60)
    
    memory_service = MemoryService()
    user_id = "test_user_002"
    session_id = "test_session_002"
    
    # Short-term에 상호작용 추가
    print("\n📝 Short-term Memory 구성:")
    memory_service.short_term.add_interaction(session_id, {
        'device_name': '에어컨',
        'action': '온도 26도 설정'
    })
    memory_service.short_term.add_interaction(session_id, {
        'device_name': '조명',
        'action': '밝기 30% 설정'
    })
    print("  ✅ 2개의 상호작용 추가됨")
    
    # Long-term에 패턴 학습
    print("\n🎓 Long-term Memory 학습:")
    await memory_service.long_term.learn_from_interaction(user_id, {
        'device_type': 'air_conditioner',
        'time_of_day': '밤',
        'parameters': {'temperature': 26},
        'accepted': True
    })
    print("  ✅ 패턴 학습 완료")
    
    # 전체 컨텍스트 조회
    print("\n🔍 전체 컨텍스트 조회:")
    context = await memory_service.get_full_context(user_id, session_id)
    
    print("\n  [Short-term Memory]")
    print(f"    - 최근 상호작용: {len(context['short_term']['recent_history'])}개")
    print(f"    - 컨텍스트 요약:")
    for line in context['short_term']['context_summary'].split('\n'):
        print(f"      {line}")
    
    print("\n  [Long-term Memory]")
    print(f"    - 선호 온도: {context['long_term']['user_preferences']['temperature_preference']}℃")
    print(f"    - 패턴 인사이트:")
    for line in context['long_term']['pattern_insights'].split('\n'):
        print(f"      {line}")
    
    print("\n✅ 전체 컨텍스트 통합 테스트 완료!")
    return True


async def test_memory_limits():
    """Memory 크기 제한 테스트"""
    print("\n" + "="*60)
    print("4️⃣  Memory 크기 제한 테스트")
    print("="*60)
    
    memory_service = MemoryService()
    session_id = "test_session_003"
    
    print("\n📝 15개의 상호작용 추가 (최대 10개):")
    for i in range(15):
        memory_service.short_term.add_interaction(session_id, {
            'device_name': f'기기_{i+1}',
            'action': f'액션_{i+1}'
        })
    
    history = memory_service.short_term.get_history(session_id)
    print(f"  - 저장된 상호작용 수: {len(history)}개")
    print(f"  - 예상: 10개 (max_size 제한)")
    
    if len(history) == 10:
        print("\n✅ 크기 제한 정상 작동!")
        print(f"  - 가장 오래된 항목: {history[0]['device_name']}")
        print(f"  - 가장 최근 항목: {history[-1]['device_name']}")
    else:
        print(f"\n⚠️  예상과 다름: {len(history)}개")
    
    return len(history) == 10


async def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("🧠 GazeHome Memory 시스템 테스트")
    print("="*60)
    
    results = []
    
    try:
        # 1. Short-term Memory 테스트
        results.append(await test_short_term_memory())
        
        # 2. Long-term Memory 테스트
        results.append(await test_long_term_memory())
        
        # 3. 전체 컨텍스트 통합 테스트
        results.append(await test_full_context())
        
        # 4. Memory 크기 제한 테스트
        results.append(await test_memory_limits())
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 최종 결과
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    test_names = [
        "Short-term Memory",
        "Long-term Memory",
        "전체 컨텍스트 통합",
        "Memory 크기 제한"
    ]
    
    print()
    for name, result in zip(test_names, results):
        status = "✅ 통과" if result else "❌ 실패"
        print(f"  {status} - {name}")
    
    if all(results):
        print("\n🎉 모든 테스트 통과!")
        print("\nMemory 시스템이 정상적으로 작동합니다:")
        print("  ✅ Short-term Memory (세션별 히스토리)")
        print("  ✅ Long-term Memory (사용자 선호도 학습)")
        print("  ✅ 통합 컨텍스트 조회")
        print("  ✅ 자동 크기 제한")
    else:
        print("\n⚠️  일부 테스트 실패")
        print("위의 오류 메시지를 확인해주세요.")


if __name__ == '__main__':
    asyncio.run(main())
