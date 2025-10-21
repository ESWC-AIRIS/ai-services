# GazeHome AI Agent Memory Architecture

## 개요

GazeHome AI Agent는 **Memory 시스템**을 통해 완전한 Agent로 작동합니다.  
Memory는 Short-term(단기)과 Long-term(장기) 두 가지로 구성되며, 개인화된 추천과 학습 능력을 제공합니다.

## 🧠 Memory 시스템 구조

```
Agent (LLMService)
├── Perception (환경 인식)
│   ├── 기기 정보
│   ├── 날씨 정보 (MCP)
│   └── 시간 정보
│
├── Memory (기억) ✨
│   ├── Short-term Memory
│   │   ├── 세션별 대화 히스토리
│   │   ├── 최근 N개 상호작용
│   │   └── 컨텍스트 요약
│   │
│   └── Long-term Memory
│       ├── 사용자 선호도
│       ├── 시간대별 패턴
│       └── MongoDB 영구 저장
│
├── Reasoning (추론)
│   └── Memory 기반 개인화 추천
│
├── Action (행동)
│   └── Memory 업데이트
│
└── Learning (학습)
    └── 피드백 기반 패턴 학습
```

---

## 📋 Short-term Memory

### 목적
- 현재 세션의 대화 맥락 유지
- 최근 상호작용 기억
- 연속된 명령어 이해

### 구현
```python
class ShortTermMemory:
    def __init__(self, max_size: int = 10):
        self.sessions: Dict[str, deque] = {}
    
    def add_interaction(self, session_id: str, interaction: Dict):
        """상호작용 추가"""
    
    def get_history(self, session_id: str, last_n: int = None):
        """히스토리 조회"""
    
    def get_context_summary(self, session_id: str):
        """컨텍스트 요약"""
```

### 저장 데이터
```python
interaction = {
    'device_id': 'ac_001',
    'device_name': '거실 에어컨',
    'device_type': 'air_conditioner',
    'action': 'set_temperature',
    'intent': '온도 조절',
    'timestamp': '2025-10-08T23:50:00',
    'accepted': True  # 피드백
}
```

### 사용 예시
```python
# 1번째 상호작용
사용자: "에어컨 클릭"
Agent: "에어컨 켜고 26도로 설정할까요?"

# 2번째 상호작용 (Short-term Memory 활용)
사용자: "조명 클릭"
Agent: "방금 에어컨을 켜셨는데, 조명도 어둡게 해드릴까요?"
      ↑ Short-term Memory에서 "에어컨 켰음" 기억
```

### 특징
- ✅ 메모리 내 저장 (빠름)
- ✅ 세션별 독립 관리
- ✅ 자동 크기 제한 (기본 10개)
- ✅ 오래된 세션 자동 정리 (24시간)

---

## 🎯 Long-term Memory

### 목적
- 사용자 선호도 학습
- 시간대별 패턴 파악
- 장기적인 개인화

### 구현
```python
class LongTermMemory:
    def __init__(self, db_service=None):
        self.db_service = db_service
        self.user_preferences: Dict[str, Dict] = {}
    
    async def get_user_preferences(self, user_id: str):
        """사용자 선호도 조회"""
    
    async def update_user_preference(self, user_id: str, data: Dict):
        """선호도 업데이트"""
    
    async def learn_from_interaction(self, user_id: str, interaction: Dict):
        """상호작용에서 학습"""
    
    async def get_pattern_insights(self, user_id: str, context: Dict):
        """패턴 기반 인사이트"""
```

### 저장 데이터 (MongoDB)
```python
user_preference = {
    'user_id': 'user_123',
    'temperature_preference': 24,  # 선호 온도
    'brightness_preference': 70,   # 선호 밝기
    'favorite_devices': ['ac_001', 'light_001'],
    'time_patterns': {
        '아침': {
            'light': [{'brightness': 80}, {'brightness': 85}],
            'curtain': [{'open': True}]
        },
        '밤': {
            'air_conditioner': [{'temperature': 26}, {'temperature': 25}],
            'light': [{'brightness': 30}]
        }
    }
}
```

### 학습 프로세스
```python
# 1. 사용자가 추천 수락
사용자: "에어컨 26도" → 수락 ✅

# 2. Long-term Memory 학습
await memory.long_term.learn_from_interaction(user_id, {
    'device_type': 'air_conditioner',
    'time_of_day': '밤',
    'parameters': {'temperature': 26},
    'accepted': True
})

# 3. 패턴 업데이트
time_patterns['밤']['air_conditioner'].append({'temperature': 26})

# 4. 다음 추천에 반영
"이 시간대에 자주 26도로 설정하시네요. 오늘도 26도로 할까요?"
```

### 특징
- ✅ MongoDB 영구 저장
- ✅ 사용자별 독립 관리
- ✅ 피드백 기반 학습
- ✅ 시간대별 패턴 분석
- ✅ 캐싱으로 빠른 조회

---

## 🔄 Memory 통합 흐름

### 1. 추천 생성 시
```python
async def generate_device_recommendation(device_info, context):
    # 1. Perception
    weather = await mcp_client.get_weather()
    
    # 2. Memory 조회
    memory_context = await self.memory.get_full_context(user_id, session_id)
    short_term_summary = memory_context['short_term']['context_summary']
    long_term_insights = memory_context['long_term']['pattern_insights']
    
    # 3. Reasoning (Memory 정보 포함)
    prompt = f"""
    ## Short-term Memory
    {short_term_summary}
    
    ## Long-term Memory
    {long_term_insights}
    
    위 Memory 정보를 활용하여 개인화된 추천을 생성하세요.
    """
    
    # 4. Action & Memory Update
    result = await self.llm.ainvoke(prompt)
    self.memory.short_term.add_interaction(session_id, interaction)
    
    return result
```

### 2. 피드백 처리 시
```python
async def update_feedback(user_id, session_id, interaction_id, accepted):
    # 1. Short-term Memory에서 상호작용 찾기
    history = self.memory.short_term.get_history(session_id)
    
    # 2. 피드백 업데이트
    interaction['accepted'] = accepted
    
    # 3. Long-term Memory 학습
    await self.memory.long_term.learn_from_interaction(user_id, interaction)
```

---

## 📊 Memory 활용 예시

### 시나리오 1: 반복 패턴 학습

**1주차**:
```
월요일 밤 10시: 에어컨 26도 → 수락 ✅
화요일 밤 10시: 에어컨 26도 → 수락 ✅
수요일 밤 10시: 에어컨 26도 → 수락 ✅
```

**2주차**:
```
월요일 밤 10시: 에어컨 클릭
Agent: "매번 이 시간에 26도로 설정하시네요. 오늘도 26도로 할까요?"
      ↑ Long-term Memory 패턴 활용
```

### 시나리오 2: 연속 명령 이해

**Short-term Memory 활용**:
```
1. 사용자: "에어컨 클릭" → "에어컨 켜고 26도"
2. 사용자: "온도 조절" → "방금 26도로 설정했는데, 몇 도로 변경할까요?"
   ↑ Short-term Memory: "방금 에어컨 26도 설정함" 기억
```

### 시나리오 3: 개인화 추천

**Long-term Memory 활용**:
```
사용자 A: 항상 밤에 26도 선호
사용자 B: 항상 밤에 24도 선호

같은 상황에서도 다른 추천:
- A에게: "26도로 설정할까요?" (선호도 반영)
- B에게: "24도로 설정할까요?" (선호도 반영)
```

---

## 🔧 Memory 관리

### 설정
```python
# Short-term Memory 크기 조정
memory = ShortTermMemory(max_size=20)  # 기본 10개

# 세션 정리 주기 조정
memory.cleanup_old_sessions(max_age_hours=48)  # 기본 24시간
```

### 모니터링
```python
# Memory 상태 확인
history = memory.short_term.get_history(session_id)
print(f"현재 세션 상호작용 수: {len(history)}")

# 사용자 선호도 확인
prefs = await memory.long_term.get_user_preferences(user_id)
print(f"선호 온도: {prefs['temperature_preference']}℃")
```

### 초기화
```python
# 세션 삭제
memory.short_term.clear_session(session_id)

# 사용자 선호도 초기화
await memory.long_term.update_user_preference(user_id, {
    'temperature_preference': 24,
    'time_patterns': {}
})
```

---

## 🎓 학술적 배경

### Agent의 Memory 분류

**1. Sensory Memory (감각 기억)**
- 현재 입력 데이터
- GazeHome: Perception 단계에서 처리

**2. Short-term Memory (단기 기억)**
- 작업 기억 (Working Memory)
- 제한된 용량 (7±2 항목, Miller's Law)
- GazeHome: 10개 상호작용 저장

**3. Long-term Memory (장기 기억)**
- 무제한 용량
- 영구 저장
- GazeHome: MongoDB + 패턴 학습

### 참고 문헌
- **ReAct** (Reasoning + Acting): LLM Agent 패러다임
- **MemGPT**: LLM의 Memory 관리 기법
- **LangChain Memory**: 대화 히스토리 관리

---

## 🚀 향후 확장

### 1. Vector DB 통합 (RAG)
```python
# Semantic Memory
memory.vector_db.add_interaction(interaction)
similar = memory.vector_db.search_similar(query)
```

### 2. Episodic Memory
```python
# 특정 에피소드 기억
memory.episodic.add_episode({
    'date': '2025-10-08',
    'event': '폭염 주의보',
    'actions': ['에어컨 22도로 설정']
})
```

### 3. Collaborative Memory
```python
# 가족 구성원 간 Memory 공유
family_prefs = memory.get_family_preferences(family_id)
```

---

## 📝 요약

**현재 GazeHome Agent**:
```
✅ Perception (환경 인식)
✅ Memory (단기 + 장기 기억)
✅ Reasoning (LLM 추론)
✅ Action (명령 생성)
✅ Learning (피드백 학습)
```

**완전한 Agent 조건 충족!** 🎉

Memory 시스템을 통해:
- 개인화된 추천 제공
- 사용자 패턴 학습
- 컨텍스트 유지
- 연속된 대화 이해

GazeHome AI Agent는 이제 **학술적으로 완전한 Memory-enabled Agent**입니다!

