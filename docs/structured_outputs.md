# structured_outputs.py

## 개요

LLM의 출력을 **구조화된 형식(Structured Output)** 으로 받기 위한 Pydantic 모델을 정의합니다.
`invoke_llm`의 `response_format` 파라미터에 전달하여 사용합니다.

---

## 클래스

### `WebsiteData`

회사 웹사이트 스크래핑 후 LLM이 추출하는 구조화 데이터입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `summary` | str | 회사 웹사이트 내용 요약 |
| `blog_url` | str | 회사 블로그 메인 URL |
| `youtube` | str | YouTube 채널 링크 |
| `twitter` | str | Twitter 계정 링크 |
| `facebook` | str | Facebook 페이지 링크 |

**사용 위치:** `nodes.py` → `review_company_website()` 함수

```python
website_info = invoke_llm(
    system_prompt=WEBSITE_ANALYSIS_PROMPT,
    user_message=content,
    model="gpt-4o-mini",
    response_format=WebsiteData   # ← 여기서 사용
)
# website_info.blog_url, website_info.youtube 등으로 접근
```

---

### `EmailResponse`

개인화 이메일 생성 시 LLM이 반환하는 구조화 데이터입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `subject` | str | 이메일 제목 (수신자가 열어보도록 유도) |
| `email` | str | 리드 프로필에 맞춘 개인화 이메일 본문 |

**사용 위치:** `nodes.py` → `generate_personalized_email()` 함수

```python
output = invoke_llm(
    system_prompt=PERSONALIZE_EMAIL_PROMPT,
    user_message=lead_data,
    model="gpt-4o-mini",
    response_format=EmailResponse   # ← 여기서 사용
)
subject = output.subject
email_body = output.email
```

---

## 활용 방식

LangChain의 `with_structured_output()` 메서드를 통해 LLM이 항상 정해진 형식으로 응답하도록 강제합니다.
JSON 파싱 오류 없이 필드에 바로 접근할 수 있어 안정적입니다.
