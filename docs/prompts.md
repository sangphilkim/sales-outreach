# prompts.py

## 개요

LLM 호출 시 사용하는 **모든 시스템 프롬프트(System Prompt)** 를 모아놓은 파일입니다.
`nodes.py`에서 `from .prompts import *` 방식으로 전체 임포트하여 사용합니다.

---

## 프롬프트 목록

### `WEBSITE_ANALYSIS_PROMPT`

**용도:** 회사 웹사이트 HTML 스크래핑 결과를 분석
**출력 형식:** `WebsiteData` (구조화 출력)
**변수:** `{main_url}` — 분석 대상 웹사이트 URL

주요 작업:
- 웹사이트 내용 500단어 요약
- 블로그 URL 추출
- YouTube, Twitter, Facebook 링크 추출

---

### `LEAD_SEARCH_REPORT_PROMPT`

**용도:** 리드의 LinkedIn 프로필과 회사 정보를 종합하여 비즈니스 프로필 리포트 생성
**출력 형식:** 마크다운 문자열
**변수:** 없음

리포트 포함 항목:
- 회사 개요 (이름, 산업, 규모, 미션, 제품/서비스)
- 리드 프로필 요약 (경력, 학력, 스킬, 주요 인사이트, 운영 관련성)

---

### `BLOG_ANALYSIS_PROMPT`

**용도:** 회사 블로그 내용을 분석하여 성과 리포트 생성
**출력 형식:** 마크다운 문자열
**변수:** `{company_name}` — 분석 대상 회사명

리포트 포함 항목:
- 블로그 요약 (게시물 수, 활성도, 주요 주제)
- 점수 (게시물 수 / 활성도 / 관련성, 각 1-10점)
- 개선 기회 (콘텐츠 갭, 새 주제, 콘텐츠 포맷)
- 실행 계획 (3-5가지 추천 사항)

---

### `YOUTUBE_ANALYSIS_PROMPT`

**용도:** 회사 YouTube 채널을 분석하여 성과 리포트 생성
**출력 형식:** 마크다운 문자열
**변수:** `{company_name}` — 분석 대상 회사명

리포트 포함 항목:
- 채널 요약 (영상 수, 활성도, 참여도, 주요 주제)
- 점수 (영상 수 / 활성도 / 참여도 / 관련성, 각 1-10점)
- 개선 기회 및 실행 계획

---

### `NEWS_ANALYSIS_PROMPT`

**용도:** 최근 뉴스를 분석하여 회사 관련 주요 사실 추출
**출력 형식:** 마크다운 문자열 (3섹션 구조)
**변수:** `{company_name}`, `{number_months}`, `{date}`

출력 구조:
- **Recent News Summary** — 관련 뉴스 bullet list (날짜 포함)
- **RIAD-Relevant Signals** — 호텔 소싱·이벤트·MICE·숙박 관련 항목만 (해당 없으면 생략)
- **Assessment** — 1-2문장: RIAD 솔루션 필요성 시사 여부

**엣지 케이스:** 관련 뉴스 없으면 `"No relevant news found for {company_name} in the past {number_months} months."` 만 반환

---

### `DIGITAL_PRESENCE_REPORT_PROMPT`

**용도:** 블로그, 소셜 미디어, 뉴스 분석 결과를 종합하여 디지털 프레즌스 리포트 생성
**출력 형식:** 마크다운 문자열
**변수:** `{company_name}`

리포트 포함 항목:
- Executive Summary (전체 현황 요약)
- 플랫폼별 분석 (Blog, Facebook, Twitter, YouTube)
- 최근 뉴스 요약
- 전체 개선 권고안

---

### `GLOBAL_LEAD_RESEARCH_REPORT_PROMPT`

**용도:** 리드 프로필, 회사 정보, 디지털 프레즌스 리포트를 통합하여 종합 분석 리포트 생성
**출력 형식:** 마크다운 문자열
**변수:** `{company_name}`

리포트 포함 항목:
- **0. Executive Qualification Summary** (2-3문장: strong/moderate/weak fit 판정 + 핵심 근거)
- I. 리드 프로필 (현재 역할, 경력, 관심사)
- II. 회사 개요 (산업, 미션, 제품/서비스, 시장 포지셔닝)
- III. 참여 이력 (최근 뉴스, 소셜 미디어 활동)
- IV. Hotel Sourcing & Event Operations Assessment (이벤트·숙박 운영 규모, 현재 툴/방식, 페인 포인트, RIAD 타겟 고객 적합도)

**데이터 처리 규칙:**
- LinkedIn과 웹사이트 정보 충돌 시 명시적으로 불일치 표기
- 데이터 부족 시 "Insufficient data available" 기재 (추측 금지)

---

### `SCORE_LEAD_PROMPT`

**용도:** 글로벌 리서치 리포트를 기반으로 리드 적합성 점수(1-10) 산출
**출력 형식:** `FINAL SCORE: X.X` 형식으로 마지막 줄에 출력 → `nodes.py`에서 정규식으로 파싱
**사용 모델:** `gpt-4o` (고품질 판단)

평가 기준 (각 1-10점, CoT 추론 후 점수):
1. 산업 및 역할 적합성 (여행사, DMC, 이벤트 기획사, MICE 회사 등 RIAD 핵심 타겟 여부)
2. 비즈니스 활동 규모 (호텔 제안서 볼륨, 이벤트 빈도, 숙박 수요 규모)
3. 회사 규모 (10-200명 소·중형 = 10점, 500명 이상 대기업 = 낮은 점수)
4. 성장 신호 (신규 클라이언트, 신시장 진출, 파트너십, 채용 등)
5. 기술 성숙도 (전문 호텔 소싱·이벤트 숙박 플랫폼 미보유 여부 — yeyak/Ria event 도입 여지)
6. 콘텐츠 및 디지털 활동 (블로그·소셜·뉴스 노출 — 사업 규모 및 신뢰도 간접 지표)

**데이터 부족 처리:** 특정 기준에 데이터 불충분 시 3점(보수적 기본값) 부여 후 명시
**중요:** 최종 점수가 7 이상이면 `check_if_qualified`에서 "qualified"로 분류됨

---

### `GENERATE_OUTREACH_REPORT_PROMPT`

**용도:** 리드 회사를 위한 맞춤형 아웃리치 리포트 생성
**출력 형식:** 마크다운 문자열
**사용 모델:** `gpt-4o`

리포트 구성 (5개 섹션):
1. Introduction — RIAD Corporation 소개
2. Business Analysis — 회사 개요, 발견된 과제, 개선 기회
3. Relevant RIAD Solutions — yeyak/Ria event 맞춤형 솔루션 제안
4. Expected Results and ROI — 케이스 스터디 기반 예상 성과
5. Call to Action — 다음 단계 안내

---

### `PROOF_READER_PROMPT`

**용도:** 생성된 아웃리치 리포트를 교정 및 품질 검토
**출력 형식:** 수정된 마크다운 문자열

검토 항목:
- 5개 섹션 구조 완전성 확인
- 링크 유효성 및 누락 여부
- 언어 명확성 및 전문성 개선

---

### `PERSONALIZE_EMAIL_PROMPT`

**용도:** 리드 프로필 기반 개인화 콜드 아웃리치 이메일 생성
**출력 형식:** `EmailResponse` (구조화 출력 — 제목 + 본문)

가이드라인:
- 리드의 최근 경험/회사 정보 참조한 1-2줄 개인화 섹션 포함
- 대화체이면서 전문적인 톤
- 가정이나 과장 없이 근거 기반 작성

---

### `GENERATE_SPIN_QUESTIONS_PROMPT`

**용도:** SPIN 셀링 방법론 기반 맞춤형 질문 생성
**출력 형식:** 질문 목록 문자열

SPIN 구성 (카테고리별 2-3개, 총 8-12개):
- **S**ituation (2-3개) — 현재 상황 파악 질문
- **P**roblem (2-3개) — 문제점 발굴 질문
- **I**mplication (2-3개) — 문제의 영향 탐색 질문
- **N**eed-Payoff (2-3개) — 해결책의 가치 확인 질문

---

### `WRITE_INTERVIEW_SCRIPT_PROMPT`

**용도:** SPIN 질문과 리드 정보를 바탕으로 영업 전화 인터뷰 스크립트 생성
**출력 형식:** 마크다운 형식의 스크립트

스크립트 구성 (10-15분 분량 / 1,200-1,800 words):
- **Introduction** — 인사
- **Discovery** — 현황 파악 질문
- **Pain Exploration** — 문제·영향 탐색
- **Solution Fit** — RIAD 솔루션 연결
- **Close / Next Steps** — 미팅 제안

플레이스홀더: `[LEAD_NAME]`, `[COMPANY_NAME]`
