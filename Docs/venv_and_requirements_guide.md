# Python 가상환경 & `requirements.txt` 운용 가이드

> 목표 : 재현 가능한 배포를 위해 **프로젝트별 `venv` + 고정된 의존성**을 설정

## 가상환경
### Python 가상환경 생성
```bash
python -m venv .venv
```

### 가상환경 활성화
**Windows / Bash**
```bash
source .venv/Scripts/activate
```

**macOS / Bash**
```bash
source .venv/bin/activate
```