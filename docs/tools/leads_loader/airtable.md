# airtable.py

## 개요

**Airtable을 CRM으로 사용**하는 리드 로더입니다.
pyairtable 라이브러리를 통해 Airtable 테이블에서 리드를 조회하고 업데이트합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `pyairtable` | Airtable Python SDK |
| `pyairtable.formulas.match` | Airtable 필터 수식 |
| `LeadLoaderBase` | 추상 기본 클래스 |

---

## 클래스: `AirtableLeadLoader`

### 초기화

```python
loader = AirtableLeadLoader(
    access_token="patXXXXXXXXXXXXXX",
    base_id="appXXXXXXXXXXXXXX",
    table_name="Leads"
)
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `access_token` | str | Airtable Personal Access Token |
| `base_id` | str | Airtable Base ID (`app`으로 시작) |
| `table_name` | str | 테이블 이름 |

---

## 메서드

### `fetch_records(lead_ids=None, status_filter="NEW")`

Airtable에서 리드 레코드를 가져옵니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `lead_ids` | list \| None | `None` | 특정 레코드 ID 목록 |
| `status_filter` | str | `"NEW"` | `Status` 필드로 필터링할 값 |

**동작 방식:**
- `lead_ids` 있을 때: 각 ID로 개별 레코드 조회
- `lead_ids` 없을 때: `Status == status_filter`인 레코드 전체 조회

**반환값:** 리드 dict 목록 (`{"id": 레코드ID, 필드명: 값, ...}`)

---

### `update_record(lead_id, updates)`

Airtable 레코드를 업데이트합니다. 기존 필드는 유지하면서 지정한 필드만 변경합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lead_id` | str | Airtable 레코드 ID (`rec`으로 시작) |
| `updates` | dict | 업데이트할 필드명: 값 쌍 |

**동작 방식:**
1. 현재 레코드 조회
2. 기존 필드에 새 필드 병합 (새 필드 동적 추가 가능)
3. Airtable API로 업데이트

**반환값:** 업데이트된 레코드 dict

**예외:** 레코드 ID가 존재하지 않으면 `ValueError` 발생

---

## 환경변수 / 설정

Airtable 연결 정보는 환경변수로 관리하는 것을 권장합니다:

```python
import os
loader = AirtableLeadLoader(
    access_token=os.getenv("AIRTABLE_ACCESS_TOKEN"),
    base_id=os.getenv("AIRTABLE_BASE_ID"),
    table_name=os.getenv("AIRTABLE_TABLE_NAME")
)
```

---

## Airtable 테이블 요구 형식

| 컬럼 | 설명 |
|------|------|
| `Status` | 리드 상태 (`NEW`, `ATTEMPTED_TO_CONTACT` 등) |
| `First Name` | 리드 이름 |
| `Last Name` | 리드 성 |
| `Email` | 이메일 주소 |
| `Phone` | 전화번호 |

---

## 사용 예시

```python
from src.tools.leads_loader.airtable import AirtableLeadLoader

loader = AirtableLeadLoader(
    access_token="patXXXXXX",
    base_id="appXXXXXX",
    table_name="Leads"
)

# 신규 리드 가져오기
leads = loader.fetch_records(status_filter="NEW")

# 리드 업데이트
loader.update_record("recXXXXXX", {
    "Status": "ATTEMPTED_TO_CONTACT",
    "Score": "8.5",
    "Last Contacted": "2025-01-15"
})
```

---

## 주의사항

- Airtable Personal Access Token은 Airtable 계정 설정에서 생성합니다.
- `update_record`는 레코드가 없을 때 `ValueError`를 발생시킵니다. 호출부에서 예외 처리가 필요합니다.
- `Status` 필드명이 정확히 일치해야 필터링이 동작합니다.
- 새 필드는 업데이트 시 Airtable 테이블에 자동으로 추가되지 않습니다. Airtable에서 먼저 컬럼을 생성해야 합니다.
