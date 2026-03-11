# google_docs_tools.py

## 개요

Google Drive API와 Google Docs API를 사용하여 **Google 문서를 생성, 조회, 폴더 관리**하는 도구입니다.
리포트를 Google Docs에 저장하고 공유 링크를 생성하는 데 사용됩니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `googleapiclient.discovery` | Google API 클라이언트 |
| `googleapiclient.http.MediaFileUpload` | 파일 업로드 |
| `src.utils.get_google_credentials` | Google OAuth 인증 정보 |

---

## 클래스: `GoogleDocsManager`

### 초기화

```python
manager = GoogleDocsManager()
```

- `self.docs_service` — Google Docs API v1 서비스
- `self.drive_service` — Google Drive API v3 서비스

---

## 메서드

### `add_document(content, doc_title, folder_name, make_shareable, folder_shareable, markdown)`

Google 문서를 생성하고 지정된 폴더에 저장합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `content` | str | - | 문서 내용 |
| `doc_title` | str | - | 문서 제목 |
| `folder_name` | str | - | 저장할 Google Drive 폴더명 |
| `make_shareable` | bool | `False` | 문서를 링크로 공유 가능하게 설정 |
| `folder_shareable` | bool | `False` | 폴더를 링크로 공유 가능하게 설정 |
| `markdown` | bool | `False` | `True`이면 마크다운 파일로 업로드하여 Google Doc으로 변환 |

**반환값:**
- 성공 시:
  ```python
  {
      "document_url": "https://docs.google.com/document/d/{id}",
      "shareable_url": "https://...",  # make_shareable=True일 때
      "folder_url": "https://drive.google.com/..."
  }
  ```
- 실패 시: `None`

---

### `get_document(doc_url)`

Google Docs URL로 문서 내용을 가져옵니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `doc_url` | str | Google Docs 문서 URL |

**반환값:** 문서 전체 텍스트 내용 str / 실패 시 `None`

---

### `_get_or_create_folder(folder_name, make_shareable)` *(내부 메서드)*

지정된 이름의 Google Drive 폴더를 찾거나 없으면 생성합니다.

**반환값:** `(folder_id, folder_url)` 튜플

---

### `_make_document_shareable(doc_id)` *(내부 메서드)*

문서를 "링크가 있는 모든 사용자가 볼 수 있음" 상태로 변경합니다.

**반환값:** 공유 가능한 문서 URL str

---

### `_convert_markdown_to_google_doc(markdown_content, title)` *(내부 메서드)*

마크다운 내용을 Google Document로 변환합니다.

**동작 방식:**
1. 마크다운 내용을 임시 파일 `temp_markdown.md`로 저장
2. Google Drive에 마크다운 파일 업로드 (Google Docs로 자동 변환)
3. 임시 파일 삭제

**반환값:** 생성된 문서 ID str

---

## 환경변수

Google OAuth 인증에 필요한 파일:

| 파일 | 설명 |
|------|------|
| `credentials.json` | Google Cloud Console OAuth 클라이언트 파일 |
| `token.json` | 최초 인증 후 자동 생성되는 토큰 파일 |

---

## 사용 예시

```python
from src.tools.google_docs_tools import GoogleDocsManager

manager = GoogleDocsManager()

# 마크다운 리포트 저장 (공유 링크 포함)
result = manager.add_document(
    content="# 리포트\n\n내용...",
    doc_title="Outreach Report",
    folder_name="JohnDoe_Acme",
    make_shareable=True,
    folder_shareable=True,
    markdown=True
)

if result:
    print(f"문서 URL: {result['document_url']}")
    print(f"공유 링크: {result['shareable_url']}")
    print(f"폴더 링크: {result['folder_url']}")
```

---

## 주의사항

- `add_document` 실패 시 예외를 raise하지 않고 `None`을 반환합니다. 호출부에서 `None` 체크가 필요합니다.
- 마크다운 변환은 임시 파일(`temp_markdown.md`)을 생성하고 자동으로 삭제합니다.
- 폴더가 없으면 자동으로 생성합니다.
- 동일한 이름의 폴더가 여러 개 있으면 첫 번째 폴더를 사용합니다.
- `folder_name`에 `'` (apostrophe)가 포함된 경우 Drive API 쿼리용으로 자동 이스케이프 처리됩니다 (예: `O'Brien` → `O\'Brien`).
