# utils.py

## 개요

프로젝트 전반에서 공통으로 사용하는 **유틸리티 함수 모음**입니다.
Google OAuth 인증, LLM 호출 추상화, 리포트 저장 등 핵심 기능을 제공합니다.

---

## Google API 스코프

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',       # Gmail 수정
    'https://www.googleapis.com/auth/spreadsheets',       # Google Sheets
    'https://www.googleapis.com/auth/documents',          # Google Docs
    'https://www.googleapis.com/auth/drive',              # Google Drive
    'https://www.googleapis.com/auth/youtube.readonly'    # YouTube 읽기
]
```

---

## 함수

### `get_current_date()`

현재 날짜를 `"YYYY-MM-DD"` 형식의 문자열로 반환합니다.

**반환값:** str (예: `"2025-01-15"`)

---

### `get_google_credentials()`

Google OAuth 2.0 인증 정보를 반환합니다.

**동작 방식:**
1. `token.json` 파일이 있으면 로드
2. 토큰이 만료된 경우 자동 갱신
3. 토큰이 없으면 브라우저를 통한 OAuth 인증 진행 후 `token.json` 저장

**필요 파일:**
- `credentials.json` — Google Cloud Console에서 발급한 OAuth 클라이언트 파일
- `token.json` — 최초 인증 후 자동 생성

**반환값:** Google OAuth `Credentials` 객체

---

### `get_report(reports, report_name)`

리포트 목록에서 제목으로 특정 리포트의 내용을 찾아 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `reports` | list[Report] | 리포트 목록 |
| `report_name` | str | 찾을 리포트 제목 |

**반환값:** 리포트 본문 str / 없으면 `""`

---

### `save_reports_locally(reports)`

모든 리포트를 `reports/` 폴더에 `.txt` 파일로 저장합니다.
폴더가 없으면 자동으로 생성합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `reports` | list[Report] | 저장할 리포트 목록 |

**저장 경로:** `reports/{report.title}.txt`

---

### `get_llm_by_provider(llm_provider, model)`

LLM 프로바이더명과 모델명을 받아 LangChain LLM 객체를 반환합니다.

| 프로바이더 | 값 | LangChain 클래스 |
|-----------|-----|----------------|
| OpenAI | `"openai"` | `ChatOpenAI` |
| Anthropic | `"anthropic"` | `ChatAnthropic` |
| Google | `"google"` | `ChatGoogleGenerativeAI` |

**temperature:** 모든 프로바이더 공통 `0.1` (안정적인 출력)

---

### `invoke_llm(system_prompt, user_message, model, llm_provider, response_format)`

LLM을 호출하는 **통합 추상화 함수**입니다. 프로젝트 전반에서 LLM 호출 시 이 함수를 사용합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `system_prompt` | str | - | 시스템 프롬프트 |
| `user_message` | str | - | 사용자 메시지 |
| `model` | str | `"gpt-4o-mini"` | 사용할 모델명 |
| `llm_provider` | str | `"openai"` | LLM 프로바이더 |
| `response_format` | Pydantic 클래스 \| None | `None` | 구조화 출력 형식 |

**반환값:**
- `response_format`이 없으면: 문자열 (str)
- `response_format`이 있으면: 해당 Pydantic 객체

**사용 예시:**
```python
# 문자열 출력
result = invoke_llm(
    system_prompt="You are an analyst.",
    user_message="Analyze this company.",
    model="gpt-4o-mini"
)

# 구조화 출력
from src.structured_outputs import WebsiteData
result = invoke_llm(
    system_prompt="Extract data.",
    user_message=content,
    model="gpt-4o-mini",
    response_format=WebsiteData
)
```
