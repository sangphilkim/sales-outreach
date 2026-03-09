# markdown_scraper_tool.py

## 개요

웹 페이지 URL을 입력받아 HTML을 **마크다운(Markdown) 형식**으로 변환하여 반환하는 도구입니다.
리드의 블로그나 회사 홈페이지 내용을 LLM이 처리하기 쉬운 텍스트로 변환하는 데 사용됩니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `requests` | HTTP 요청 라이브러리 |
| `BeautifulSoup` | HTML 파싱 라이브러리 |
| `html2text` | HTML → 마크다운 변환 라이브러리 |
| `re` | 정규식 (불필요한 줄바꿈 제거용) |

---

## 함수

### `scrape_website_to_markdown(url)`

지정된 URL의 웹 페이지를 요청하여 마크다운 문자열로 변환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `url` | str | 스크래핑할 웹 페이지 주소 |

**반환값:** 마크다운으로 변환된 페이지 본문 (str)

**예외:** HTTP 요청 실패 시 `Exception` 발생
```
Exception: Failed to fetch the URL. Status code: 404
```

---

## 동작 방식

```
URL 입력
  ↓
requests.get() 으로 HTML 가져오기
  ↓
BeautifulSoup 으로 HTML 파싱
  ↓
html2text 로 마크다운 변환
  ↓
정규식으로 불필요한 빈 줄 제거
  ↓
마크다운 문자열 반환
```

---

## 변환 설정

| 옵션 | 값 | 설명 |
|------|-----|------|
| `ignore_links` | False | 링크를 마크다운 형식으로 유지 |
| `ignore_images` | True | 이미지 태그 제거 |
| `ignore_tables` | True | 테이블 태그 제거 |

---

## 사용 예시

```python
from src.tools.base.markdown_scraper_tool import scrape_website_to_markdown

content = scrape_website_to_markdown("https://example.com/blog/post-1")
print(content)
```

---

## 주의사항

- 일부 웹 사이트는 봇 차단(Bot Block) 정책으로 인해 스크래핑이 실패할 수 있습니다.
- User-Agent 헤더를 설정하여 일반 브라우저처럼 요청하지만 모든 사이트에서 동작을 보장하지 않습니다.
- JavaScript로 렌더링되는 동적 페이지(SPA)는 내용을 제대로 가져오지 못할 수 있습니다.
- 연속 빈 줄(`\n\n\n` 이상)은 자동으로 `\n\n`으로 정리됩니다.
