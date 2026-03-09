# gmail_tools.py

## 개요

Gmail API를 사용하여 이메일 초안을 생성하거나 이메일을 직접 발송하는 도구입니다.
Google OAuth 인증 정보를 기반으로 Gmail 서비스에 연결합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `googleapiclient` | Google API 클라이언트 라이브러리 |
| `email.mime.text` | 이메일 메시지 포맷 생성 |
| `src.utils.get_google_credentials` | Google OAuth 인증 정보 반환 함수 |

---

## 클래스: `GmailTools`

### 초기화

```python
gmail = GmailTools()
```

- `get_google_credentials()`를 통해 OAuth 인증 정보를 가져옴
- Gmail API v1 서비스 객체를 생성하여 `self.service`에 저장

---

## 메서드

### `create_draft_email(recipient, subject, email_content)`

Gmail에 이메일 **초안**을 저장합니다. 실제로 발송하지는 않습니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `recipient` | str | 수신자 이메일 주소 |
| `subject` | str | 이메일 제목 |
| `email_content` | str | 이메일 본문 내용 |

**반환값:** 생성된 draft 객체 (dict) / 실패 시 `None`

---

### `send_email(recipient, subject, email_content)`

이메일을 **즉시 발송**합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `recipient` | str | 수신자 이메일 주소 |
| `subject` | str | 이메일 제목 |
| `email_content` | str | 이메일 본문 내용 |

**반환값:** 발송된 메시지 객체 (dict) / 실패 시 `None`

---

### `_create_message(recipient, subject, text)` *(내부 메서드)*

`MIMEText` 객체를 생성하여 이메일 메시지 형식으로 변환합니다.

---

### `_encode_message(message)` *(내부 메서드)*

`MIMEText` 객체를 Base64 URL-safe 인코딩된 문자열로 변환합니다.
Gmail API가 요구하는 `raw` 포맷입니다.

---

## 사용 예시

```python
gmail = GmailTools()

# 초안 저장
gmail.create_draft_email(
    recipient="lead@example.com",
    subject="안녕하세요",
    email_content="반갑습니다. 연락드립니다."
)

# 즉시 발송
gmail.send_email(
    recipient="lead@example.com",
    subject="안녕하세요",
    email_content="반갑습니다. 연락드립니다."
)
```

---

## 주의사항

- Google OAuth 인증이 사전에 완료되어 있어야 합니다.
- 이메일 발송 실패 시 예외를 raise하지 않고 `None`을 반환하며 에러 메시지를 출력합니다.
- 현재 plain text 형식만 지원합니다 (`MIMEText`).
