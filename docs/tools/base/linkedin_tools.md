# linkedin_tools.py

## 개요

LinkedIn 프로필 URL을 추출하고, RapidAPI를 통해 LinkedIn 프로필 데이터를 스크래핑하는 도구입니다.
개인 프로필과 회사 프로필 모두 지원합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `re` | 정규식 라이브러리 |
| `requests` | HTTP 요청 라이브러리 |
| `src.utils.invoke_llm` | LLM 호출 추상화 함수 |
| `RAPIDAPI_KEY` | 환경변수 — RapidAPI 인증 키 |

---

## 함수

### `extract_linkedin_url_base(search_results)`

구글 검색 결과 목록에서 **규칙 기반**으로 LinkedIn 개인 프로필 URL을 추출합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `search_results` | list | 구글 검색 결과 리스트 |

**반환값:** LinkedIn URL 문자열 / 없으면 빈 문자열 `""`

**동작 방식 (2단계):**
1. **1차**: 검색 결과 중 `linkedin.com/in`이 포함된 URL을 직접 반환
2. **2차**: `/in/` URL이 없으면 `linkedin.com/posts/{username}_...` 패턴에서 username을 추출하여 `linkedin.com/in/{username}` URL을 구성하여 반환

---

### `extract_linkedin_url(search_results)`

구글 검색 결과 목록에서 **LLM을 사용하여** LinkedIn 개인 프로필 URL을 추출합니다.
`extract_linkedin_url_base`보다 정확하며, 여러 결과 중 올바른 URL을 판별합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `search_results` | list | 구글 검색 결과 리스트 |

**반환값:** LinkedIn URL 문자열 / 없으면 빈 문자열 `""`

**사용 모델:** `gpt-4o-mini`

**판별 기준:**
- `/in`이 포함된 URL만 유효 처리
- `/posts`, `/company`가 포함된 URL 제외

---

### `scrape_linkedin(linkedin_url, is_company=False)`

RapidAPI의 `fresh-linkedin-profile-data` 서비스를 통해 LinkedIn 프로필 데이터를 가져옵니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `linkedin_url` | str | - | 스크래핑할 LinkedIn URL |
| `is_company` | bool | `False` | `True`이면 회사 프로필, `False`이면 개인 프로필 |

**반환값:**
- 성공 시: 프로필 데이터 dict
- 실패 시: 빈 dict `{}`

**사용 API 엔드포인트:**

| `is_company` 값 | 사용 URL |
|----------------|----------|
| `False` (개인) | `fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead` |
| `True` (회사) | `fresh-linkedin-profile-data.p.rapidapi.com/get-company-by-linkedinurl` |

---

## 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|----------|------|
| `RAPIDAPI_KEY` | ✅ 필수 | RapidAPI 인증 키 |

---

## 사용 예시

```python
from src.tools.base.linkedin_tools import (
    extract_linkedin_url_base,
    extract_linkedin_url,
    scrape_linkedin
)
from src.tools.base.search_tools import google_search

# 1. 구글 검색 후 LinkedIn URL 추출 (규칙 기반)
results = google_search("John Doe CEO Acme Corp LinkedIn")
url = extract_linkedin_url_base(results)

# 2. 구글 검색 후 LinkedIn URL 추출 (LLM 기반)
url = extract_linkedin_url(results)

# 3. 개인 프로필 스크래핑
profile = scrape_linkedin("https://www.linkedin.com/in/johndoe/")

# 4. 회사 프로필 스크래핑
company = scrape_linkedin("https://www.linkedin.com/company/acme/", is_company=True)
```

---

## 주의사항

- RapidAPI는 유료 서비스입니다. 플랜에 따라 월별 호출 한도가 있습니다.
- LinkedIn 정책에 따라 스크래핑이 제한될 수 있으며, API 응답 실패 시 빈 dict `{}`를 반환합니다.
- `extract_linkedin_url_base`는 2단계 규칙 기반 방식으로, `/posts/` URL에서도 username을 추출할 수 있습니다.
- `extract_linkedin_url` (LLM 방식)은 현재 `lead_research.py`에서 사용하지 않습니다. LLM이 빈 문자열 대신 마크다운 코드블록을 반환하는 경우가 있어 `extract_linkedin_url_base`로 대체되었습니다.
