# search_tools.py

## 개요

Google Serper API를 사용하여 구글 검색 결과 및 최근 뉴스를 가져오는 도구입니다.
리드(Lead)와 회사에 대한 정보를 수집하는 데 사용됩니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `requests` | HTTP 요청 라이브러리 |
| `SERPER_API_KEY` | 환경변수 — Serper API 인증 키 |

---

## 함수

### `google_search(query)`

구글 검색을 수행하고 **유기적(organic) 검색 결과** 목록을 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `query` | str | 검색할 키워드 또는 문장 |

**반환값:** 검색 결과 리스트 (list of dict)

각 결과 항목 예시:
```json
{
  "title": "...",
  "link": "https://...",
  "snippet": "..."
}
```

**사용 API:** `https://google.serper.dev/search`

---

### `get_recent_news(company)`

특정 회사 또는 키워드와 관련된 **최근 1년치 뉴스**를 가져옵니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `company` | str | 검색할 회사명 또는 키워드 |

**반환값:**
- 성공 시: 뉴스 목록을 포맷한 문자열 (str)
- 실패 시: `"Error fetching news: {상태코드}"` 문자열

출력 포맷 예시:
```
Title: 회사 뉴스 제목
Snippet: 뉴스 요약
Date: 날짜
URL: https://...

Title: ...
```

**사용 API:** `https://google.serper.dev/news`

**검색 옵션:**
- `num: 20` — 최대 20개 뉴스 반환
- `tbs: qdr:y` — 최근 1년 이내 뉴스로 필터링
- 결과는 **최신순**으로 역정렬되어 반환됩니다

---

## 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|----------|------|
| `SERPER_API_KEY` | ✅ 필수 | Serper API 인증 키 |

---

## 사용 예시

```python
from src.tools.base.search_tools import google_search, get_recent_news

# 구글 검색
results = google_search("John Doe CEO Acme Corp LinkedIn")
for r in results:
    print(r['link'])

# 최근 뉴스 검색
news = get_recent_news("Acme Corporation")
print(news)
```

---

## 주의사항

- Serper API는 유료 서비스입니다. API 호출 횟수에 따라 비용이 발생합니다.
- `google_search`는 `organic` 결과만 반환하며, 광고나 다른 섹션은 포함되지 않습니다.
- `get_recent_news`는 HTTP 상태코드가 200이 아닐 경우 예외 없이 에러 문자열을 반환합니다.
