# hubspot.py

## 개요

**HubSpot CRM을 연동**하는 리드 로더입니다.
HubSpot API를 통해 연락처(Contacts)를 조회하고 상태를 업데이트합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `hubspot` | HubSpot Python SDK |
| `LeadLoaderBase` | 추상 기본 클래스 |
| `HUBSPOT_API_KEY` | 환경변수 — HubSpot API 액세스 토큰 |

---

## 기본 조회 필드

```python
HUBSPOT_CONTACTS_PROPERTIES = [
    "email", "firstname", "lastname",
    "hs_lead_status", "address", "phone"
]
```

---

## 클래스: `HubSpotLeadLoader`

### 초기화

```python
# 환경변수 사용
loader = HubSpotLeadLoader()

# 직접 토큰 입력
loader = HubSpotLeadLoader(access_token="pat-na1-xxxxx")
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `access_token` | str \| None | `None` | HubSpot API 액세스 토큰 (없으면 환경변수 사용) |

---

## 메서드

### `fetch_records(lead_ids=None, status_filter="NEW")`

HubSpot에서 연락처를 가져옵니다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `lead_ids` | list \| None | `None` | 특정 연락처 ID 목록 (없으면 status_filter로 조회) |
| `status_filter` | str | `"NEW"` | 필터링할 `hs_lead_status` 값 |

**동작 방식:**
- `lead_ids` 있을 때: 각 ID로 개별 조회
- `lead_ids` 없을 때: 최대 100개 연락처 조회 후 `hs_lead_status`로 필터링

**반환값:** 리드 dict 목록 (`{"id": ..., "email": ..., "firstname": ..., ...}`)

---

### `update_record(lead_id, fields_to_update)`

HubSpot 연락처의 필드를 업데이트합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `lead_id` | str | HubSpot 연락처 ID |
| `fields_to_update` | dict | 업데이트할 필드명: 값 쌍 |

**반환값:** `{"lead_id": ..., "updated_fields": ...}` / 실패 시 `None`

---

## 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|----------|------|
| `HUBSPOT_API_KEY` | ✅ 필수 | HubSpot Private App 액세스 토큰 |

---

## 사용 예시

```python
from src.tools.leads_loader.hubspot import HubSpotLeadLoader

loader = HubSpotLeadLoader()

# NEW 상태 리드 가져오기
leads = loader.fetch_records(status_filter="NEW")

# 리드 상태 업데이트
loader.update_record("12345", {
    "hs_lead_status": "ATTEMPTED_TO_CONTACT",
    "notes": "AI 분석 완료"
})
```

---

## 주의사항

- `fetch_records`는 최대 100개까지만 가져옵니다. 100개 이상의 경우 페이지네이션 구현이 필요합니다.
- HubSpot의 `hs_lead_status` 값이 이 시스템의 `status_filter` 값과 정확히 일치해야 합니다.
- HubSpot Private App 토큰을 사용해야 합니다 (OAuth App 토큰과 다름).
