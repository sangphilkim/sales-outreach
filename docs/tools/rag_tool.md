# rag_tool.py

## 개요

**RAG(Retrieval-Augmented Generation)** 기능을 제공하는 도구입니다.
`data/case_studies/` 폴더의 케이스 스터디 문서를 벡터 DB(ChromaDB)에 저장하고,
리드 정보와 가장 유사한 케이스 스터디를 검색하여 반환합니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `langchain_community.document_loaders.DirectoryLoader` | 문서 로더 |
| `langchain_openai.OpenAIEmbeddings` | OpenAI 임베딩 모델 |
| `langchain_chroma.Chroma` | ChromaDB 벡터 스토어 |
| `OPENAI_API_KEY` | 환경변수 — OpenAI API 키 |

---

## 설정

| 항목 | 값 | 설명 |
|------|-----|------|
| 벡터 DB 경로 | `database/` | ChromaDB 저장 폴더 |
| 임베딩 모델 | `text-embedding-3-small` | OpenAI 임베딩 모델 |
| 케이스 스터디 경로 | `data/case_studies/` | 원본 문서 폴더 |
| 검색 결과 수 | `k=1` | 가장 유사한 1개만 반환 |

---

## 함수

### `get_vector_store()`

ChromaDB 벡터 스토어를 가져오거나 새로 생성합니다.

**동작 방식:**
```
database/ 폴더 존재 여부 확인
  ↓
  ├─ 존재하면: 기존 벡터 DB 로드
  └─ 없으면:
       ↓
     data/case_studies/ 문서 로드
       ↓
     OpenAI 임베딩 생성
       ↓
     ChromaDB에 저장 (database/ 폴더 생성)
```

**반환값:** `Chroma` 벡터 스토어 객체

---

### `fetch_similar_case_study(description)`

입력한 설명과 가장 유사한 케이스 스터디를 검색하여 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `description` | str | 검색 기준 텍스트 (보통 리드 리서치 리포트) |

**반환값:** 가장 유사한 케이스 스터디 본문 문자열

---

## 케이스 스터디 추가 방법

1. `data/case_studies/` 폴더에 새 문서 파일 추가 (`.txt`, `.md` 등)
2. `database/` 폴더 삭제 → 다음 실행 시 자동 재생성

---

## 사용 예시

```python
from src.tools.rag_tool import fetch_similar_case_study

# 리드 리서치 리포트와 유사한 케이스 스터디 검색
lead_report = "친환경 기술 회사로 소셜 미디어 참여도가 낮고..."
case_study = fetch_similar_case_study(lead_report)
print(case_study)
```

---

## 주의사항

- 최초 실행 시 `database/` 폴더가 없으면 OpenAI 임베딩 API를 호출하여 벡터 DB를 생성합니다.
- `data/case_studies/` 폴더에 문서가 없으면 오류가 발생합니다.
- LLM 모델을 Gemini에서 OpenAI로 전환한 경우, 기존 `database/` 폴더를 삭제하고 재생성해야 합니다.
