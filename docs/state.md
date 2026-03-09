# state.py

## 개요

LangGraph 워크플로우 전체에서 공유되는 **상태(State) 데이터 모델**을 정의하는 파일입니다.
Pydantic BaseModel과 TypedDict를 사용하여 각 노드 간에 전달되는 데이터 구조를 명세합니다.

---

## 데이터 모델

### `SocialMediaLinks`

회사의 소셜 미디어 링크를 저장하는 모델입니다.

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `blog` | str | `""` | 회사 블로그 URL |
| `facebook` | str | `""` | Facebook 페이지 URL |
| `twitter` | str | `""` | Twitter 계정 URL |
| `youtube` | str | `""` | YouTube 채널 URL |

---

### `Report`

분석 결과 리포트 하나를 저장하는 모델입니다.

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `title` | str | `""` | 리포트 제목 |
| `content` | str | `""` | 리포트 본문 내용 |
| `is_markdown` | bool | `False` | 마크다운 형식 여부 |

---

### `LeadData`

처리 중인 리드(잠재 고객)의 기본 정보 모델입니다.

| 필드 | 타입 | 필수 여부 | 설명 |
|------|------|----------|------|
| `id` | str | ✅ | 리드의 고유 식별자 (CRM 행 번호 등) |
| `name` | str | ✅ | 리드의 전체 이름 |
| `address` | str | ✅ | 리드의 주소 |
| `email` | str | ✅ | 리드의 이메일 주소 |
| `phone` | str | ✅ | 리드의 전화번호 |
| `profile` | str | ✅ | LinkedIn에서 추출한 리드 프로필 요약 |

---

### `CompanyData`

리드가 속한 회사 정보를 저장하는 모델입니다.

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `name` | str | `""` | 회사명 |
| `profile` | str | `""` | 회사 프로필 요약 |
| `website` | str | `""` | 회사 웹사이트 URL |
| `social_media_links` | SocialMediaLinks | 기본 객체 | 소셜 미디어 링크 모음 |

---

### `GraphInputState`

그래프 시작 시 외부에서 입력받는 초기 상태입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `leads_ids` | List[str] | 처리할 리드 ID 목록 |

---

### `GraphState`

LangGraph 전체 워크플로우에서 노드 간에 공유되는 **메인 상태 객체**입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `leads_ids` | List[str] | 처리할 리드 ID 목록 |
| `leads_data` | List[dict] | 로드된 리드 데이터 목록 |
| `current_lead` | LeadData | 현재 처리 중인 리드 |
| `lead_score` | str | LLM이 부여한 리드 점수 (예: "8.5") |
| `company_data` | CompanyData | 현재 리드의 회사 정보 |
| `reports` | Annotated[list[Report], add] | 생성된 리포트 목록 (병렬 fan-out 누적) |
| `reports_folder_link` | str | Google Drive 리포트 폴더 링크 |
| `custom_outreach_report_link` | str | 개인화 아웃리치 리포트 링크 |
| `personalized_email` | str | 생성된 개인화 이메일 내용 |
| `interview_script` | str | 생성된 인터뷰 스크립트 |
| `number_leads` | int | 남은 처리 리드 수 |

---

## 핵심 설계

### `Annotated[list[Report], add]` — 병렬 fan-out 누적 패턴

```python
reports: Annotated[list[Report], add]
```

- LangGraph에서 여러 노드가 **동시에 실행**될 때, 각 노드의 `reports` 반환값이 **덮어쓰이지 않고 누적(append)** 됩니다.
- `analyze_blog_content`, `analyze_social_media_content`, `analyze_recent_news` 3개 노드가 동시에 실행되어 각각 리포트를 생성합니다.
- `operator.add`가 reducer 역할을 하여 리스트를 합칩니다.
