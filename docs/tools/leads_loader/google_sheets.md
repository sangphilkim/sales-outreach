# google_sheets.py

## 개요

**Google Sheets를 CRM으로 사용**하는 리드 로더입니다.
스프레드시트에서 신규 리드를 읽어오고, 처리 후 상태를 업데이트합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `googleapiclient.discovery` | Google API 클라이언트 |
| `src.utils.get_google_credentials` | Google OAuth 인증 정보 |
| `LeadLoaderBase` | 추상 기본 클래스 |

---

## 클래스: `GoogleSheetLeadLoader`

### 초기화

```python
loader = GoogleSheetLeadLoader(spreadsheet_id="your_sheet_id")
# 또는
loader = GoogleSheetLeadLoader(spreadsheet_id="your_sheet_id", sheet_name="Leads")
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `spreadsheet_id` | str | - | Google Sheets 스프레드시트 ID |
| `sheet_name` | str | `None` | 시트 이름 (없으면 첫 번째 시트 자동 사용) |

**환경변수:** `SHEET_ID` (main.py에서 사용)

---

## 메서드

### `fetch_records(lead_ids=None, status_filter="NEW")`

Google Sheets에서 리드를 가져옵니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `lead_ids` | list \| None | `None` | 특정 리드 ID 목록 (없으면 status_filter로 조회) |
| `status_filter` | str | `"NEW"` | 가져올 상태값 |

**동작 방식:**
1. 시트 전체 데이터 가져오기
2. 첫 번째 행을 헤더로 사용
3. `lead_ids`가 있으면 해당 ID 행만 반환
4. 없으면 `Status` 컬럼이 `status_filter`인 행만 반환
5. 각 레코드에 행 번호를 `"id"`로 추가

**반환값:** 리드 dict 목록

---

### `update_record(id, fields_to_update)`

지정한 행의 여러 필드를 한 번에 업데이트합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | str | 업데이트할 행 번호 (ID) |
| `fields_to_update` | dict | 업데이트할 필드명: 값 쌍 |

**동작 방식:**
1. 헤더 행에서 컬럼 인덱스 확인
2. 각 필드를 해당 열 위치로 매핑
3. `batchUpdate`로 한 번에 업데이트 (API 호출 최소화)

**반환값:** `{"id": id, "updated_fields": fields_to_update}`

---

### `_get_sheet_name_from_id()` *(내부 메서드)*

스프레드시트 ID로 첫 번째 시트 이름을 자동으로 가져옵니다.

---

## Google Sheets 스프레드시트 요구 형식

| 컬럼 | 설명 |
|------|------|
| `First Name` | 리드 이름 |
| `Last Name` | 리드 성 |
| `Email` | 이메일 주소 |
| `Phone` | 전화번호 |
| `Address` | 주소 |
| `Status` | 상태 (`NEW`, `ATTEMPTED_TO_CONTACT` 등) |
| `Score` | 리드 점수 (업데이트됨) |
| `Analysis Reports` | Google Drive 폴더 링크 (업데이트됨) |
| `Outreach Report` | 아웃리치 리포트 링크 (업데이트됨) |
| `Last Contacted` | 마지막 연락 날짜 (업데이트됨) |

---

## 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|----------|------|
| `SHEET_ID` | ✅ 필수 | Google Sheets 스프레드시트 ID |

---

## 사용 예시

```python
import os
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader

loader = GoogleSheetLeadLoader(spreadsheet_id=os.getenv("SHEET_ID"))

# 신규 리드 가져오기
leads = loader.fetch_records(status_filter="NEW")

# 리드 상태 업데이트
loader.update_record("3", {
    "Status": "ATTEMPTED_TO_CONTACT",
    "Score": "8.5",
    "Last Contacted": "2025-01-15"
})
```

---

## 주의사항

- 컬럼이 Z(26번째) 이후로 넘어가면 `chr(65 + col_index)` 변환이 올바른 열 문자를 반환하지 못합니다 (AA, AB 등 두 글자 열은 지원 안됨).
- 시트 첫 번째 행은 반드시 헤더여야 합니다.
- `Status` 컬럼이 없는 경우 필터링이 동작하지 않습니다.
