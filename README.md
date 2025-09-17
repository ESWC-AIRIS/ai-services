# GazeHome AI Services

**시선으로 제어하는 스마트 홈 AI 서버**

아이트래킹 기술과 대형 언어 모델을 결합하여, 사용자의 시선만으로 LG 스마트 가전 및 다양한 IoT 기기를 직관적으로 제어할 수 있는 AIoT 통합 솔루션입니다.

## 🚀 주요 기능

- **시선 기반 제어**: 아이트래킹을 통한 직관적인 기기 제어
- **맥락 분석**: 사용자 상황, 환경, 선호도를 종합 분석
- **의도 추론**: LLM을 활용한 정확한 사용자 의도 파악
- **자동화 플래너**: 최적의 제어 시나리오 자동 설계
- **실시간 반영**: 사용자 이력, 날씨, 일정 등 실시간 정보 반영
- **품질 관리**: LangSmith/LangFuse를 통한 LLM 추론 모니터링

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python
- **LLM**: LangChain + Gemini API
- **Database**: MongoDB
- **Vector DB**: ChromaDB (RAG)
- **Monitoring**: LangSmith, LangFuse
- **Deployment**: Uvicorn

## 📚 문서

프로젝트 관련 상세 문서들은 `Docs/` 폴더에서 확인할 수 있습니다:

- [`gazehome_architecture.md`](Docs/gazehome_architecture.md) - GazeHome AI 서버 아키텍처 및 구조 문서
- [`git_convention.md`](Docs/git_convention.md) - Git 커밋 컨벤션 가이드
- [`venv_and_requirements_guide.md`](Docs/venv_and_requirements_guide.md) - 가상환경 및 의존성 관리 가이드

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키들을 설정
```

### 3. 서버 실행
```bash
python main.py
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해 주세요.