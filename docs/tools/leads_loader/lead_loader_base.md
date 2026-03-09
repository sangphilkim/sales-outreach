# lead_loader_base.py

## 개요

모든 CRM 로더 클래스가 상속해야 하는 **추상 기본 클래스(Abstract Base Class)** 입니다.
HubSpot, Airtable, Google Sheets 등 다양한 CRM에서 리드를 가져오는 공통 인터페이스를 정의합니다.

---

## 클래스: `LeadLoaderBase` *(ABC)*

### 허용 상태값

```python
available_statuses = ["NEW", "UNQUALIFIED", "ATTEMPTED_TO_CONTACT"]
```

| 상태 | 설명 |
|------|------|
| `NEW` | 신규 리드 (아직 처리 전) |
| `UNQUALIFIED` | 자격 미달 리드 |
| `ATTEMPTED_TO_CONTACT` | 연락 시도 완료 |

---

## 추상 메서드 (반드시 구현 필요)

### `fetch_records(status_filter="NEW")`

CRM에서 레코드를 가져오는 메서드입니다. 서브클래스에서 반드시 구현해야 합니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `status_filter` | str | `"NEW"` | 필터링할 상태값 |

**반환값:** 리드 레코드 목록 (list of dict)

---

### `update_record(lead_id, status)`

CRM 레코드의 상태를 업데이트하는 메서드입니다. 서브클래스에서 반드시 구현해야 합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lead_id` | str | 업데이트할 레코드 ID |
| `status` | str | 새로운 상태값 |

---

## 구현된 메서드

### `fetch_new_leads()`

`status_filter="NEW"` 조건으로 신규 리드를 가져옵니다.
에러 발생 시 빈 리스트를 반환합니다.

**반환값:** 신규 리드 목록 (list of dict)

---

### `update_lead_status(lead_id, status)`

상태값을 검증한 후 CRM 레코드를 업데이트합니다.
유효하지 않은 상태값이면 업데이트하지 않고 `None`을 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lead_id` | str | 업데이트할 레코드 ID |
| `status` | str | 새로운 상태값 (`available_statuses` 중 하나) |

**반환값:** 업데이트 결과 / 실패 시 `None`

---

## 상속 구조

```
LeadLoaderBase (ABC)
├── GoogleSheetLeadLoader   ← Google Sheets CRM
├── HubSpotLeadLoader       ← HubSpot CRM
└── AirtableLeadLoader      ← Airtable CRM
```

---

## 새로운 CRM 추가 방법

```python
from .lead_loader_base import LeadLoaderBase

class MyCustomCRMLoader(LeadLoaderBase):
    def __init__(self, api_key):
        self.client = MyCustomCRMClient(api_key)

    def fetch_records(self, status_filter="NEW"):
        # CRM에서 레코드 가져오는 로직 구현
        ...
        return records

    def update_record(self, lead_id, status):
        # CRM 레코드 업데이트 로직 구현
        ...
```
