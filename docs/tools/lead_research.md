# lead_research.py

## 개요

리드(잠재 고객)의 **LinkedIn 프로필을 검색, 스크래핑, 요약**하는 도구입니다.
이메일 주소에서 회사명을 추출하고 구글 검색 → LinkedIn URL 추출 → 프로필 스크래핑의 파이프라인으로 동작합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `src.utils.invoke_llm` | LLM 호출 추상화 함수 |
| `base.search_tools.google_search` | 구글 검색 |
| `base.linkedin_tools.extract_linkedin_url_base` | 규칙 기반 LinkedIn URL 추출 |
| `base.linkedin_tools.scrape_linkedin` | LinkedIn 프로필 스크래핑 |

---

## 내부 프롬프트

### `SUMMARIZE_LINKEDIN_PROFILE`

LinkedIn 스크래핑 데이터를 기반으로 **300단어 리드 프로필 요약**을 생성합니다.

- 직책, 전문성, 현재 포커스에 집중
- 가정이나 과장 없이 사실 기반 작성
- 세일즈팀이 미팅 전 참고용으로 활용

---

## 함수

### `extract_company_name(email)`

이메일 주소에서 도메인 기반으로 회사명을 추출합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `email` | str | 리드의 이메일 주소 |

**반환값:** 도메인 문자열 (예: `"acme.com"`) / 실패 시 `"Company not found"`

```python
extract_company_name("john@acme.com")  # → "acme.com"
```

---

### `research_lead_on_linkedin(lead_name, lead_email)`

리드의 LinkedIn 프로필을 검색하고 스크래핑하여 요약 정보를 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lead_name` | str | 리드의 전체 이름 |
| `lead_email` | str | 리드의 이메일 주소 |

**반환값:**
- 성공 시: 튜플 `(profile_summary, company_name, company_website, company_linkedin_url)`
- 실패 시: 에러 메시지 문자열

**처리 파이프라인:**
```
이메일 → 회사명(도메인) 추출
  ↓
구글 검색: "LinkedIn {리드이름} {회사도메인}"
  ↓
규칙 기반 LinkedIn URL 추출
  (1차: /in/ URL 직접 탐색 → 2차: /posts/ URL에서 username 추출)
  ↓
URL 유효성 검사 (빈 값 또는 linkedin.com/in/ 형식 아닌 경우 중단)
  ↓
LinkedIn 개인 프로필 스크래핑
  ↓
핵심 정보 구조화 (경력, 학력, 스킬, 자격증 등)
  ↓
회사 웹사이트 URL 정규화 (스킴 없는 경우 https:// 자동 추가)
  ↓
LLM으로 300단어 프로필 요약 생성
  ↓
(profile_summary, company_name, company_website, company_linkedin_url) 반환
```

---

## 추출하는 LinkedIn 데이터 필드

| 카테고리 | 포함 필드 |
|----------|----------|
| 기본 정보 | `full_name`, `location`, `city`, `country`, `about` |
| 스킬 | `skills` |
| 현재 회사 | `company`, `company_industry`, `join_month`, `join_year` |
| 학력 | `school`, `field_of_study`, `degree`, `date_range` |
| 경력 | `company`, `title`, `date_range`, `is_current`, `description` |
| 자격증 | `name`, `issuer`, `date` |
| 조직 활동 | `name`, `role`, `date_range` |
| 봉사 활동 | `organization`, `role`, `date_range`, `description` |
| 수상 내역 | `name`, `issuer`, `date`, `description` |

---

## 사용 예시

```python
from src.tools.lead_research import research_lead_on_linkedin

result = research_lead_on_linkedin("John Doe", "john@acme.com")

if isinstance(result, str):
    print(f"조회 실패: {result}")
else:
    profile, company_name, company_website, company_linkedin = result
    print(f"프로필 요약: {profile[:100]}...")
    print(f"회사명: {company_name}")
```
