# graph.py

## 개요

LangGraph의 `StateGraph`를 사용하여 **아웃리치 자동화 워크플로우**를 정의하고 컴파일하는 파일입니다.
각 노드(작업 단계)와 엣지(흐름)를 연결하여 전체 파이프라인을 구성합니다.

---

## 클래스: `OutReachAutomation`

### 초기화

```python
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader

loader = GoogleSheetLeadLoader(spreadsheet_id="your_sheet_id")
automation = OutReachAutomation(loader)
```

- `loader`: `LeadLoaderBase`를 상속한 CRM 로더 (GoogleSheets, HubSpot, Airtable 등)
- 초기화 시 `build_graph()`를 자동 호출하여 컴파일된 앱을 `self.app`에 저장

---

## 워크플로우 구조

```
[START]
  ↓
get_new_leads               → CRM에서 신규 리드 목록 로드
  ↓
check_for_remaining_leads   → 처리할 리드가 있는지 확인
  ↓ (조건 분기)
  ├─ "No more leads" → [END]
  └─ "Found leads"
       ↓
fetch_linkedin_profile_data   → LinkedIn 프로필 스크래핑
       ↓
review_company_website        → 회사 웹사이트 스크래핑 및 분석
       ↓
collect_company_information   → 회사 정보 수집 (fan-out 시작점)
       ↓
  ┌────┴────┬──────────────┐
analyze_blog  analyze_social  analyze_recent
_content      _media_content  _news
  └────┬────┴──────────────┘ (병렬 실행)
       ↓
generate_digital_presence_report   → 디지털 프레즌스 통합 리포트
       ↓
generate_full_lead_research_report → 전체 리드 분석 리포트
       ↓
score_lead                         → 리드 점수 산출 (1-10)
  ↓ (조건 분기)
  ├─ "not qualified" → save_reports_to_google_docs → update_CRM → (루프)
  └─ "qualified"
       ↓
generate_custom_outreach_report    → 맞춤형 아웃리치 리포트 생성
       ↓
create_outreach_materials          → 아웃리치 자료 생성 (fan-out 시작점)
       ↓
  ┌────┴────────────────────┐
generate_personalized_email  generate_interview_script
  └────┬────────────────────┘ (병렬 실행)
       ↓
await_reports_creation             → 병렬 작업 완료 대기
       ↓
save_reports_to_google_docs        → 리포트 저장 (로컬 + Google Docs)
       ↓
update_CRM                         → CRM 레코드 업데이트
       ↓
check_for_remaining_leads          → 다음 리드 처리 (루프)
```

---

## 조건부 엣지

### `check_if_there_more_leads`

| 반환값 | 다음 노드 |
|--------|----------|
| `"Found leads"` | `fetch_linkedin_profile_data` |
| `"No more leads"` | `END` |

### `check_if_qualified`

| 반환값 | 다음 노드 |
|--------|----------|
| `"qualified"` (점수 ≥ 6) | `generate_custom_outreach_report` |
| `"not qualified"` (점수 < 6) | `save_reports_to_google_docs` |

---

## 병렬 실행 구간

LangGraph는 동일한 소스 노드에서 여러 엣지가 뻗어나가면 **자동으로 병렬 실행**합니다.

| 병렬 구간 | 동시 실행 노드 |
|----------|--------------|
| 회사 분석 | `analyze_blog_content`, `analyze_social_media_content`, `analyze_recent_news` |
| 아웃리치 자료 | `generate_personalized_email`, `generate_interview_script` |

---

## 사용 예시

```python
from src.graph import OutReachAutomation
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader

loader = GoogleSheetLeadLoader(spreadsheet_id="your_sheet_id")
automation = OutReachAutomation(loader)

# 워크플로우 실행
result = automation.app.invoke(
    {"leads_ids": []},
    config={"recursion_limit": 100}
)
```
