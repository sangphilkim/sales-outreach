# company_research.py

## 개요

회사의 **LinkedIn 프로필을 스크래핑**하고, 웹사이트 정보와 결합하여 **회사 프로필 요약**을 생성하는 도구입니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `src.utils.invoke_llm` | LLM 호출 추상화 함수 |
| `base.linkedin_tools.scrape_linkedin` | LinkedIn 프로필 스크래핑 |

---

## 내부 프롬프트

### `CREATE_COMPANY_PROFILE`

LinkedIn 회사 프로필과 웹사이트 내용을 기반으로 **300단어 회사 프로필**을 생성합니다.

포함 항목:
- 회사 설명 및 가치 제안
- 타겟 고객
- 제품/서비스
- 위치, 규모, 설립 연도

---

## 함수

### `research_lead_company(linkedin_url)`

회사 LinkedIn 페이지를 스크래핑하여 구조화된 회사 정보를 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `linkedin_url` | str | 회사 LinkedIn URL |

**반환값:**
- 성공 시: 회사 정보 dict
- 실패 시: `"LinkedIn profile not found"` 문자열

**반환 dict 구조:**

| 필드 | 설명 |
|------|------|
| `company_name` | 회사명 |
| `description` | 회사 설명 |
| `year_founded` | 설립 연도 |
| `industries` | 산업 목록 |
| `specialties` | 전문 분야 |
| `employee_count` | 직원 수 |
| `social_metrics.follower_count` | LinkedIn 팔로워 수 |
| `locations` | 사무실 위치 목록 |

---

### `generate_company_profile(company_linkedin_info, scraped_website)`

LinkedIn 회사 정보와 웹사이트 스크래핑 내용을 결합하여 **LLM 기반 회사 프로필 요약**을 생성합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `company_linkedin_info` | dict \| str | LinkedIn 스크래핑 결과 |
| `scraped_website` | str | 웹사이트 스크래핑 요약 내용 |

**반환값:** 300단어 회사 프로필 요약 문자열

**사용 모델:** `gpt-4o-mini`

---

## 사용 예시

```python
from src.tools.company_research import research_lead_company, generate_company_profile

# 회사 LinkedIn 스크래핑
company_info = research_lead_company("https://www.linkedin.com/company/acme/")

# 웹사이트 + LinkedIn 정보로 프로필 생성
profile = generate_company_profile(
    company_linkedin_info=company_info,
    scraped_website="회사 웹사이트 요약..."
)
print(profile)
```

---

## 주의사항

- LinkedIn 스크래핑 실패 시(`"data"` 키 없음) 즉시 에러 문자열을 반환합니다.
- LinkedIn 데이터와 웹사이트 데이터 중 하나만 있어도 프로필 생성이 가능합니다.
- 데이터가 모두 없을 경우 LLM은 `"No company info available."` 을 반환합니다.
