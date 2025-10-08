# Weather MCP 가이드

## 📋 개요

GazeHome AI 서비스에 Weather MCP (Model Context Protocol) 서버를 구현했습니다. 이를 통해 AI 추천 시스템이 실시간 날씨 정보를 활용하여 더 정확한 추천을 제공할 수 있습니다.

## 🏗️ 구조

```
RecommendationAgent (LLM Service)
    ↓ MCP Protocol
MCP Client
    ↓
Weather MCP Server
    ↓ HTTP API
OpenWeatherMap API
```

## 📁 파일 구조

```
app/mcp/
├── __init__.py                 # MCP 모듈 초기화
├── weather_mcp_server.py       # Weather MCP 서버
└── mcp_client.py              # MCP 클라이언트

examples/
└── test_weather_mcp.py        # 테스트 스크립트
```

## 🔧 설정

### 1. 환경 변수 설정

`.env` 파일에 Weather API 키를 추가하세요:

```bash
# Weather API (OpenWeatherMap)
WEATHER_API_KEY=your_openweathermap_api_key_here
```

### 2. API 키 발급

1. [OpenWeatherMap](https://openweathermap.org/api) 가입
2. API 키 발급 (무료 플랜으로도 충분)
3. `.env` 파일에 추가

### 3. 의존성 설치

```bash
pip install httpx==0.25.2
```

## 🚀 사용 방법

### 1. 직접 Weather MCP Server 사용

```python
from app.mcp import weather_mcp_server

# 현재 날씨 조회
weather = await weather_mcp_server.get_current_weather("Seoul,KR")
print(weather)

# 날씨 경보 조회
alerts = await weather_mcp_server.get_weather_alerts("Seoul,KR")
print(alerts)

# 날씨 요약
summary = await weather_mcp_server.get_weather_summary("Seoul,KR")
print(summary)
```

### 2. MCP Client 사용

```python
from app.mcp import mcp_client

# 편의 메서드 사용
weather = await mcp_client.get_weather("Seoul,KR")
alerts = await mcp_client.get_weather_alerts("Seoul,KR")
summary = await mcp_client.get_weather_summary("Seoul,KR")

# 직접 도구 호출
result = await mcp_client.call_tool(
    "weather", 
    "get_current_weather", 
    {"location": "Seoul,KR"}
)
```

### 3. LLM 서비스에서 자동 사용

```python
from app.services.llm_service import LLMService

llm_service = LLMService()

# 날씨 정보가 자동으로 포함된 추천 생성
recommendation = await llm_service.generate_device_recommendation(
    device_info, context
)
```

## 📊 API 응답 형식

### get_current_weather

```json
{
  "location": "Seoul",
  "country": "KR",
  "temperature": 28.1,
  "feels_like": 31.2,
  "humidity": 62,
  "pressure": 1013,
  "description": "맑음",
  "main": "Clear",
  "wind_speed": 2.1,
  "visibility": 10.0,
  "timestamp": "2024-01-15T14:30:00Z",
  "source": "openweathermap"
}
```

### get_weather_alerts

```json
[
  {
    "type": "heat_warning",
    "level": "high",
    "message": "폭염주의보",
    "description": "기온이 35.0℃로 매우 높습니다."
  }
]
```

### get_weather_summary

```
"Seoul 현재 28.1℃, 맑음, 습도 62%"
```

## 🧪 테스트

### 테스트 스크립트 실행

```bash
python examples/test_weather_mcp.py
```

### 테스트 내용

1. **Weather MCP Server 직접 테스트**
   - 현재 날씨 조회
   - 날씨 경보 조회
   - 날씨 요약

2. **MCP Client 테스트**
   - 서버 목록 조회
   - 도구 목록 조회
   - 편의 메서드 테스트

3. **MCP 도구 호출 테스트**
   - 정상 도구 호출
   - 에러 케이스 테스트

4. **LLM 통합 테스트**
   - 날씨 정보가 포함된 추천 생성

## 🔄 동작 원리

### 1. API 키가 있는 경우

```
1. OpenWeatherMap API 호출
2. 실시간 날씨 데이터 수신
3. 데이터 정리 및 반환
```

### 2. API 키가 없는 경우

```
1. 모의 데이터 반환
2. 로그에 경고 메시지 출력
3. 서비스는 정상 동작
```

## 🎯 LLM 추천에 미치는 영향

### 이전 (날씨 정보 없음)
```
"에어컨을 켜시겠습니까?"
```

### 현재 (날씨 정보 포함)
```
"현재 28.1℃로 더운 날씨입니다. 에어컨을 24℃로 켜시겠습니까?"
```

## 🚨 주의사항

### 1. API 키 관리
- `.env` 파일에 API 키 저장
- Git에 커밋하지 않도록 주의
- `.gitignore`에 `.env` 포함 확인

### 2. API 제한
- OpenWeatherMap 무료 플랜: 1분당 60회 호출
- 과도한 호출 시 제한될 수 있음

### 3. 에러 처리
- API 장애 시 모의 데이터로 fallback
- 네트워크 타임아웃: 10초
- HTTP 오류 시 로그 기록

## 🔮 향후 확장

### 1. 추가 MCP 서버들
```python
# Device MCP Server
device_mcp_server = DeviceMCPServer()

# Sensor MCP Server  
sensor_mcp_server = SensorMCPServer()

# User MCP Server
user_mcp_server = UserMCPServer()
```

### 2. 고급 기능
- 날씨 예보 (5일)
- 위치별 날씨
- 날씨 알림
- 캐싱 시스템

### 3. 다른 날씨 API 지원
- AccuWeather
- WeatherAPI
- 기상청 API

## 📞 문의

Weather MCP 관련 문의사항이 있으시면 개발팀에 연락주세요.

**문서 작성일**: 2025-10-08
