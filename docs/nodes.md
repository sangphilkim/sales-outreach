# nodes.py

## 개요

LangGraph 워크플로우의 **각 단계(노드)를 구현하는 핵심 파일**입니다.
`OutReachAutomationNodes` 클래스 안에 모든 노드 함수가 정의되어 있습니다.

---

## 전역 설정

| 상수 | 기본값 | 설명 |
|------|--------|------|
| `SEND_EMAIL_DIRECTLY` | `False` | `True`로 설정 시 이메일 직접 발송 (현재 비활성) |
| `SAVE_TO_GOOGLE_DOCS` | `False` | `True`로 설정 시 리포트를 Google Docs에 저장 |

---

## 클래스: `OutReachAutomationNodes`

### 초기화

```python
nodes = OutReachAutomationNodes(loader)
```

| 속성 | 설명 |
|------|------|
| `self.lead_loader` | CRM 로더 객체 (GoogleSheets, HubSpot 등) |
| `self.docs_manager` | `GoogleDocsManager` 인스턴스 |

---

## 노드 함수 목록

### 1. `get_new_leads(state)`

CRM에서 신규 리드를 가져와 `LeadData` 객체 목록으로 변환합니다.

**반환:** `{"leads_data": [...], "number_leads": N}`

---

### 2. `check_for_remaining_leads(state)` *(static)*

처리할 리드 목록에서 다음 리드를 꺼내 `current_lead`에 설정합니다.

**반환:** `{"current_lead": LeadData}`

---

### 3. `check_if_there_more_leads(state)` *(static)*

남은 리드 수를 확인하는 **조건 분기 함수**입니다.

**반환:** `"Found leads"` 또는 `"No more leads"`

---

### 4. `fetch_linkedin_profile_data(state)`

리드의 LinkedIn 프로필과 회사 LinkedIn 프로필을 스크래핑합니다.

**동작:**
1. 리드 이름 + 이메일로 구글 검색 → LinkedIn URL 추출
2. LinkedIn 개인 프로필 스크래핑 → LLM으로 300단어 요약 생성
3. 회사 LinkedIn URL 추출 → 회사 프로필 스크래핑

**실패 처리:** LinkedIn 조회 실패 시 오류 출력 후 빈 프로필로 계속 진행

**반환:** `{"current_lead": ..., "company_data": ..., "reports": None}`
> `reports: None` 반환은 `reports_reducer`를 통해 리포트 목록을 `[]`로 초기화하는 신호입니다. 새 리드 처리 시작 시 이전 리드의 리포트를 지웁니다.

---

### 5. `review_company_website(state)`

회사 웹사이트를 스크래핑하고 분석합니다.

**동작:**
1. 웹사이트 HTML → 마크다운 변환
2. LLM으로 요약 + 소셜 미디어 링크 추출 (`WebsiteData`)
3. 회사 프로필 업데이트
4. 리드+회사 정보 기반 "General Lead Research Report" 생성

**사용 프롬프트:** `WEBSITE_ANALYSIS_PROMPT`, `LEAD_SEARCH_REPORT_PROMPT`

**반환:** `{"company_data": ..., "reports": [General Lead Research Report]}`

---

### 6. `collect_company_information(state)` *(static)*

병렬 fan-out을 위한 **중간 집결 노드**입니다. (실제 동작 없음)

**반환:** `{"reports": []}`

---

### 7. `analyze_blog_content(state)`

회사 블로그를 스크래핑하고 LLM으로 분석합니다.

**동작:** 블로그 URL이 있는 경우 스크래핑 후 "Blog Analysis Report" 생성

**사용 프롬프트:** `BLOG_ANALYSIS_PROMPT`

**반환:** `{"reports": [Blog Analysis Report]}` (블로그 없으면 빈 리스트)

---

### 8. `analyze_social_media_content(state)`

회사의 YouTube 채널을 분석합니다. (Facebook, Twitter는 미구현 TODO)

**동작:** YouTube URL이 있는 경우 YouTube API로 통계 수집 후 "Youtube Analysis Report" 생성

**사용 프롬프트:** `YOUTUBE_ANALYSIS_PROMPT`

**반환:** `{"company_data": ..., "reports": [Youtube Analysis Report]}`

---

### 9. `analyze_recent_news(state)`

Serper API로 최근 6개월 뉴스를 수집하고 분석합니다.

**사용 프롬프트:** `NEWS_ANALYSIS_PROMPT`

**반환:** `{"reports": [News Analysis Report]}`

---

### 10. `generate_digital_presence_report(state)`

Blog, Social Media, News 분석 결과를 통합하여 종합 디지털 프레즌스 리포트를 생성합니다.

**사용 프롬프트:** `DIGITAL_PRESENCE_REPORT_PROMPT`

**반환:** `{"reports": [Digital Presence Report]}`

---

### 11. `generate_full_lead_research_report(state)`

General Lead Research Report + Digital Presence Report를 합쳐 최종 글로벌 리서치 리포트를 생성합니다.

**사용 프롬프트:** `GLOBAL_LEAD_RESEARCH_REPORT_PROMPT`

**반환:** `{"reports": [Global Lead Analysis Report]}`

---

### 12. `score_lead(state)` *(static)*

글로벌 리서치 리포트를 기반으로 리드 점수(1-10)를 산출합니다.

**사용 모델:** `gpt-4o`
**사용 프롬프트:** `SCORE_LEAD_PROMPT`

**반환:** `{"lead_score": "8.5"}`

---

### 13. `check_if_qualified(state)` *(static)*

리드 점수를 파싱하여 합격/불합격을 결정하는 **조건 분기 함수**입니다.

**동작:**
1. 정규식(`\d+\.?\d*`)으로 점수 문자열에서 숫자 추출
2. `float` 변환 후 `>= 7`이면 합격 처리
3. 파싱/변환 실패 시 불합격 처리 (안전 처리)

**반환:** `"qualified"` 또는 `"not qualified"`

---

### `is_lead_qualified(state)` *(향후 확장용 — 현재 비활성)*

> 현재 코드에 주석 처리된 상태로 보존되어 있습니다.

향후 `is_qualified` 상태를 `GraphState`에 저장하여 `update_CRM` 등 하위 노드에서 자격 여부를 참조할 때 활성화합니다.

**활성화 조건:**
- `state.py`에 `is_qualified: bool` 필드 추가
- `graph.py`에서 `score_lead → is_lead_qualified → check_if_qualified` 순으로 연결

---

### 14. `create_outreach_materials(state)` *(static)*

아웃리치 자료 병렬 생성을 위한 **중간 집결 노드**입니다. (실제 동작 없음)

**반환:** `{"reports": []}`

---

### 15. `generate_custom_outreach_report(state)`

리드 회사를 위한 맞춤형 아웃리치 리포트를 생성하고 Google Docs에 저장합니다.

**동작:**
1. RAG로 유사 케이스 스터디 검색
2. `gpt-4o`로 아웃리치 리포트 초안 생성
3. `gpt-4o-mini`로 교정 및 링크 수정
4. Google Docs에 저장 후 공유 링크 반환
   - 폴더명: `f"{lead.name.strip()} ({lead.id})"` (예: `"John Smith (rec123abc)"`)
   - 문서 자체는 공개(`make_shareable=True`), 폴더는 비공개(`folder_shareable=False`)
5. 저장 실패 시 빈 링크로 계속 진행

**사용 프롬프트:** `GENERATE_OUTREACH_REPORT_PROMPT`, `PROOF_READER_PROMPT`

**반환:** `{"custom_outreach_report_link": ..., "reports_folder_link": ...}`

---

### 16. `generate_personalized_email(state)`

리드에게 보낼 개인화 이메일을 생성하고 Gmail 초안에 저장합니다.

**동작:**
1. `gpt-4o-mini`로 이메일 제목 + 본문 생성
2. Gmail API로 초안 저장
3. `SEND_EMAIL_DIRECTLY=True`이면 즉시 발송

**사용 프롬프트:** `PERSONALIZE_EMAIL_PROMPT`
**출력 형식:** `EmailResponse` (구조화 출력)

**반환:** `{"reports": [Personalized Email]}`

---

### 17. `generate_interview_script(state)`

리드와의 영업 전화를 위한 SPIN 셀링 인터뷰 스크립트를 생성합니다.

**동작:**
1. SPIN 질문 생성 (최대 15개)
2. 질문 + 리드 정보로 전화 스크립트 생성

**사용 프롬프트:** `GENERATE_SPIN_QUESTIONS_PROMPT`, `WRITE_INTERVIEW_SCRIPT_PROMPT`

**반환:** `{"reports": [Interview Script]}`

---

### 18. `await_reports_creation(state)` *(static)*

병렬 실행 완료를 기다리는 **동기화 노드**입니다. (실제 동작 없음)

**반환:** `{"reports": []}`

---

### 19. `save_reports_to_google_docs(state)`

모든 리포트를 로컬(`reports/` 폴더)에 저장하고, 설정에 따라 Google Docs에도 저장합니다.

**조건:** `SAVE_TO_GOOGLE_DOCS=True`일 때만 Google Docs 저장
- Google Docs 저장 시 폴더명: `f"{lead.name.strip()} ({lead.id})"` — `generate_custom_outreach_report`와 동일한 폴더 사용

**반환:** `{}`

---

### 20. `update_CRM(state)`

CRM 레코드를 업데이트하고 다음 리드 처리를 위해 상태를 초기화합니다.

**업데이트 필드:**

| 필드 | 값 |
|------|-----|
| Status | `"ATTEMPTED_TO_CONTACT"` |
| Score | 리드 점수 |
| Analysis Reports | Google Drive 폴더 링크 |
| Outreach Report | 아웃리치 리포트 링크 |
| Last Contacted | 오늘 날짜 |

**반환:** `{"number_leads": N - 1}`
