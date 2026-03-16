# 점수 평가 시스템 (Scoring System)

## 개요

이 시스템에서 수치 점수를 산출하는 프롬프트는 **3개**입니다. 각 점수는 독립적으로 계산되며, `SCORE_LEAD_PROMPT`의 최종 점수만이 아웃리치 진행 여부를 결정

```
BLOG_ANALYSIS_PROMPT     → 블로그 점수 (1–10, 리포트 내 참고용)
YOUTUBE_ANALYSIS_PROMPT  → 채널 점수 (1–10, 리포트 내 참고용)
SCORE_LEAD_PROMPT        → 리드 최종 점수 (1–10, 아웃리치 분기 결정)
                              ↳ FINAL SCORE ≥ 7 → 아웃리치 진행
                              ↳ FINAL SCORE < 7 → 리포트 저장만
```

> **블로그·YouTube 점수는 SCORE_LEAD의 기준 6(디지털 활동)에 간접 반영됩니다.**
> SCORE_LEAD는 Global Lead Research Report 전체를 보고 판단하며, 그 안에 블로그·YouTube 분석 결과가 포함되어 있음

---

## 1. 블로그 점수 (`BLOG_ANALYSIS_PROMPT`)

### 산출 방식

3개 기준의 단순 평균 = 총 블로그 점수

### 평가 루브릭

| 기준 | 10점 | 7점 | 4점 | 1점 |
|---|---|---|---|---|
| **게시물 수** | 월 4개 이상 | 월 2–3개 | 월 1개 | 3개월 이상 미게시 |
| **활성도** | 매주·격주 규칙적 | 월 1회 정기 | 불규칙 | 3개월 이상 비활성 |
| **관련성** | 여행·호텔·MICE 전용 | 대부분 관련 | 일부 관련 혼재 | 관련 게시물 없음 |

#### 관련성 기준 (High Relevancy)
여행·숙박·이벤트·MICE·호텔 소싱·그룹 트래블 주제 = high relevancy

#### 벤치마크 근거
- HubSpot (13,500개 고객사 데이터): 월 16개 이상 포스팅 시 4.5배 더 많은 리드 생성
- 단, 위 수치는 대기업 기준 — 여행사·DMC는 조직 규모가 작아 **월 4개 이상이 적극적 운영**에 해당
- SEMrush: 월 16개 이상 포스팅 = 더 적게 포스팅하는 기업 대비 4.5배 리드 (일반 B2B 기준)

---

## 2. YouTube 채널 점수 (`YOUTUBE_ANALYSIS_PROMPT`)

### 산출 방식

4개 기준의 단순 평균 = 총 채널 점수

### 평가 루브릭

| 기준 | 10점 | 7점 | 4점 | 1점 |
|---|---|---|---|---|
| **영상 수** | 10개 이상 | 5–9개 | 2–4개 | 2개 미만 |
| **활성도** | 격월 이상 업로드 | 분기별 | 반기별 | 1년 이상 미업로드 |
| **참여도** | 평균 1,000+ 뷰/영상 | 200–1,000 | 50–200 | 50 미만 |
| **관련성** | 여행·호텔·MICE 전용 | 대부분 관련 | 일부 관련 혼재 | 관련 영상 없음 |

#### 벤치마크 근거
- Databox 2024 B2B 채널 분석: **200뷰/영상 = B2B 신규 채널 상위 30%**
- 현재 7점 구간(200–1,000뷰)은 데이터 기준으로 정확하게 캘리브레이션됨
- B2B 채널 구독자 전환율: 0.3–1% (소비재 1–3% 대비 낮음, Databox 2024)

---

## 3. 리드 최종 점수 (`SCORE_LEAD_PROMPT`)

### 산출 방식

**7개 기준의 가중 평균 = FINAL SCORE**

> 7개 기준 모두 구현 완료.

```
FINAL SCORE = (C1 × 0.25) + (C2 × 0.15) + (C3 × 0.15) + (C4 × 0.10)
            + (C5 × 0.10) + (C6 × 0.05) + (C7 × 0.20)
```

### 자격 판정 임계값

| FINAL SCORE | 판정 | 다음 단계 |
|---|---|---|
| ≥ 7.0 | **Qualified** | 아웃리치 리포트 + 이메일 + 인터뷰 스크립트 생성 |
| < 7.0 | **Not Qualified** | 리포트 저장 + CRM 업데이트만 |

> **📌 관찰 중 (미적용):** C1 ≤ 4(호텔 소싱이 부수적이거나 무관한 회사)인 경우에도 나머지 기준이 좋으면 FINAL SCORE ≥ 7.0이 가능함. 예: 일반 이벤트 에이전시 CEO + 성장 중 → 약 8.5점. 현재는 "다른 기준이 좋다면 아웃리치 시도 자체는 합리적"이라는 판단 하에 게이팅 조건 없이 운영 중. 실제 아웃리치 결과를 쌓은 후 C1 최소 임계값(예: C1 < 7이면 자동 탈락) 도입 여부를 재검토 예정.

---

### 기준 1. 산업 및 역할 적합성

**측정 대상:** 회사의 핵심 업무에서 호텔 소싱·이벤트 숙박이 차지하는 비중

| 점수 | 정의 | 예시 |
|---|---|---|
| 10 | 호텔 소싱·이벤트 숙박이 **핵심 서비스** (웹사이트에 명시) | DMC, 전문 행사 기획사, MICE 전문 여행사 |
| 7 | 호텔 소싱이 **주요 업무 중 하나** (서비스 목록에 포함) | 인센티브 트래블 포함 여행사, 기업 출장 관리사 |
| 4 | 호텔 소싱이 **부수적** (가끔 필요, 핵심 아님) | 웨딩 플래너, 컨퍼런스 홀 운영사, 일반 이벤트 에이전시 |
| 1 | 관련 없음 | 마케팅 에이전시, IT 회사, 제조업 |

> **데이터 부족 시:** 3점 부여 후 "Insufficient data — scored 3" 명시

---

### 기준 2. 비즈니스 활동 규모

**측정 대상:** 실제 운영 중인 이벤트·호텔 소싱 규모

| 점수 | 관측 가능한 규모 신호 |
|---|---|
| 10 | 연 30개 이상 이벤트 언급 OR 1,000+ room nights OR 클라이언트 포트폴리오 20개 이상 OR 다국가·다도시 운영 명시 |
| 7 | 연 15–29개 이벤트 OR 500–999 room nights OR 클라이언트 10–19개 |
| 4 | 연 5–14개 이벤트 OR 클라이언트 5–9개 OR 규모 신호 1개 확인 |
| 1 | 연 5개 미만 OR 규모 관련 정보 없음 |

#### 벤치마크 근거
- **Splash Events Outlook Report 2025 / Amex GBT 2026:** 이벤트 전문가 평균 연간 이벤트 수 = **29개 (2024년)**, 전년(14개) 대비 2배 증가
- 연 30개 이상 = 업계 평균 이상 → 플랫폼 도입 시 ROI가 가장 명확한 구간
- Cvent 2026: 43%의 미팅이 10명 이상 출장 수반 → 숙박 관리 복잡도 증가

---

### 기준 3. 회사 규모

**측정 대상:** LinkedIn 기준 직원 수

| 점수 | 직원 수 | 근거 |
|---|---|---|
| 10 | 20–200명 | SMB SaaS win rate 30–40% (최고), self-serve 온보딩 최적 |
| 7 | 10–19명 | 운영 가능하나 예산 제약 가능성 |
| 5 | 5–9명 | 부티크 DMC 전형, 솔루션 필요하나 팀 리소스 제한 |
| 3 | 201–500명 | 구매 프로세스 복잡, 승인 단계 증가 |
| 1 | 500명 이상 또는 1–4명 | 대기업: 커스텀 계약 필요 / 1인: 예산 없음 |

#### 벤치마크 근거
- **Pavilion 2024 B2B SaaS Performance Metrics:** SMB(<200명) win rate **30–40%**, Mid-Market **25–35%**, Enterprise **20–25%**
- **Optifai Win Rate by Deal Size 2025:** 동일 패턴 확인
- **IBISWorld 2026:** 미국 여행사 59,673개 — 대부분 소규모 운영 (DMC 추정 5–50명)
- **Close.com SMB Sales:** 200명 이하 기업에서 CEO·Founder가 직접 구매 결정 → 빠른 세일즈 사이클

---

### 기준 4. 성장 신호

**측정 방식:** 아래 5개 관측 가능한 신호 중 확인된 개수로 점수 결정

#### 카운트 대상 신호

| # | 신호 | 관측 방법 |
|---|---|---|
| ① | 신규 시장·지역 진출 발표 | 웹사이트, 뉴스, LinkedIn 포스트 |
| ② | 신규 클라이언트·파트너십 공개 | 웹사이트 케이스스터디, 뉴스, LinkedIn |
| ③ | 채용 공고 (영업·운영·이벤트 직군) | LinkedIn 채용 탭, 웹사이트 |
| ④ | 펀딩·투자 유치 | 뉴스, Crunchbase 언급 |
| ⑤ | 신규 서비스·제품 출시 | 웹사이트 업데이트, 블로그, 뉴스 |

#### 점수 매핑

| 점수 | 확인된 신호 수 |
|---|---|
| 10 | 4–5개 |
| 7 | 2–3개 |
| 4 | 1개 |
| 1 | 0개 |

#### 벤치마크 근거
- **Cognism Buying Signals (직접 확인):**
  - 펀딩 라운드 이후 → 새 솔루션 구매 가능성 **2.5배**
  - 리더십 교체 이후 → **첫 100일 내 예산의 70%** 집행
- **Zylo SaaS Trends 2026:** 헤드카운트 20%+ 성장 = 기술 도입 의향 높음
- **Bombora 2024:** Intent 신호 조합 시 pipeline 전환율 +20%

---

### 기준 5. 기술 성숙도

**측정 대상:** SaaS 도구 사용 여부 + 전문 호텔 소싱·이벤트 플랫폼 보유 여부

| 점수 | 조건 |
|---|---|
| 10 | 일반 도구만 사용 (Excel/이메일/Google Sheets) + 전문 호텔 소싱 플랫폼 없음 + SaaS 친화 신호 있음 (도구·클라우드·자동화 언급) |
| 7 | 일부 SaaS 도구 사용 (CRM, 프로젝트 관리) + 이벤트 하우징·호텔 소싱 플랫폼 없음 |
| 4 | **경쟁 플랫폼 사용 중** (Cvent, Lanyon, HRS 등) — 교체 필요 |
| 1 | 기술 신호 없음 OR 완전 커스텀 엔터프라이즈 시스템 사용 |

> **핵심 로직:** 기술이 전혀 없는 것보다 **"기술에 익숙하지만 전문 플랫폼은 없는 상태"** 가 이상적 타겟. 도입 장벽이 낮고 ROI를 빠르게 이해할 수 있음.

#### 벤치마크 근거
- **Cvent Event Statistics 2026 (직접 확인):**
  - 이벤트 전문가의 **72%**가 미팅 관리 소프트웨어 사용 (Amex GBT 2026)
  - **68%**가 CRM 연동 이벤트 플랫폼 사용 (Splash Events Outlook 2025)
  - → **28–32%는 아직 전문 플랫폼 미보유** = RIAD의 핵심 타겟 구간

---

### 기준 6. 콘텐츠 및 디지털 활동

**측정 대상:** 블로그·YouTube·뉴스 활동 수준 (앞서 계산된 점수 직접 참조)

| 점수 | 조건 |
|---|---|
| 10 | 블로그 점수 ≥ 7 **AND** YouTube 점수 ≥ 7 (또는 하나 ≥ 8 + 활성 뉴스 커버리지) |
| 7 | 블로그 점수 ≥ 7 **OR** YouTube 점수 ≥ 7 |
| 4 | 블로그 점수 4–6 또는 YouTube 점수 4–6 (일부 활동, 불규칙) |
| 1 | 두 점수 모두 < 4 또는 디지털 프레즌스 없음 |

> **설계 의도:** 기준 6은 앞선 분석의 **집계 함수** 역할. 중복 평가 없이 이미 산출된 수치를 활용.

---

### 기준 7. 의사결정권

**측정 대상:** LinkedIn 직함 기반 구매 결정 권한

| 점수 | 직함 |
|---|---|
| 10 | CEO, Founder, Co-Founder, Owner, Managing Director |
| 7 | VP, Director, Head of (Events / Travel / Operations / Procurement) |
| 5 | Senior Manager, Operations Manager, Event Manager |
| 3 | Manager (without Senior), Coordinator, Specialist |
| 1 | Intern, Assistant, Analyst OR 직함 불명확 또는 LinkedIn 데이터 없음 |

> **📌 설계 원칙:** LinkedIn 데이터가 없다고 해서 의사결정권자로 간주할 수 없음. 데이터 부재 = 1점 처리 (일반 원칙인 3점 기본값 대신 최하위 적용). 가중치 20% 특성상 패널티가 크지만(최대 1.4점 차이), 이는 의도된 결과 — 직함 정보가 확인된 리드만 높은 점수를 받도록 설계.

#### 벤치마크 근거
- **Pipedrive Lead Scoring Guide (직접 확인):** CEO 또는 Director = **최고 점수(+10)** 명시 — "they have the power to make purchasing decisions"
- **Close.com SMB Sales (직접 확인):** 200명 이하 SMB = CEO·Founder가 직접 구매 결정 (빠른 사이클)
- **HBR "Making the Consensus Sale":** B2B 구매에 평균 5.4명 서명 필요 — SMB는 이보다 훨씬 적음
- **Belkins 2025 (2,000만건 LinkedIn 아웃리치 분석):** C-suite·VP 응답률 **6.98%** (직함별 최고)

#### 구현 현황
- `SCORE_LEAD_PROMPT`에 기준 7 추가 완료
- `nodes.py` 정규식 파싱 로직 변경 불필요 (`FINAL SCORE: X.X` 앵커 유지)
- 공식: `(C1×0.25) + (C2×0.15) + (C3×0.15) + (C4×0.10) + (C5×0.10) + (C6×0.05) + (C7×0.20)`

---

## 데이터 부족 처리 원칙

모든 기준에 공통 적용:

```
특정 기준에 대한 데이터가 불충분할 경우:
→ 3점 (보수적 기본값) 부여
→ "[기준명]: Insufficient data — scored 3" 명시
→ 추측하거나 유추하지 않음
```

> **왜 3점인가:** 5점(중간값)은 낙관적 가정. 3점은 "정보 없음 = 불리한 상황"을 전제하는 보수적 접근. 실제 데이터로 검증된 리드만 높은 점수를 받도록 설계.

---

## 가중치 시스템

업계 표준(MadKudu, HockeyStack, Breadcrumbs.io) 기반 가중 평균 방식

### 적용 가중치

| 기준 | 가중치 | 이유 |
|---|---|---|
| 1. 산업 및 역할 적합성 | **25%** | 산업이 맞지 않으면 나머지 기준이 의미 없음 |
| 7. 의사결정권 | **20%** | 전환율에 가장 직접적 영향 |
| 2. 비즈니스 활동 규모 | **15%** | 플랫폼 ROI와 직결 |
| 3. 회사 규모 | **15%** | Self-serve 온보딩 가능 여부 결정 |
| 4. 성장 신호 | **10%** | 타이밍 신호 |
| 5. 기술 성숙도 | **10%** | 플랫폼 교체 장벽 판단 |
| 6. 디지털 활동 | **5%** | 간접 지표, 낮은 가중치 적절 |

### 계산 공식

```
FINAL SCORE = (C1 × 0.25) + (C2 × 0.15) + (C3 × 0.15) + (C4 × 0.10)
            + (C5 × 0.10) + (C6 × 0.05) + (C7 × 0.20)
```

### 구현 현황
- `SCORE_LEAD_PROMPT` Output Instructions에 가중치 공식 추가 완료
- `nodes.py` 파싱 로직 변경 불필요 (`FINAL SCORE: X.X` 앵커 유지)

---

## 참고 자료

| 출처 | 활용 기준 | URL |
|---|---|---|
| Splash Events Outlook Report 2025 / Amex GBT 2026 | 기준 2: 연 평균 이벤트 수 29개 | cvent.com/en/blog/events/event-statistics |
| Cvent Event Statistics 2026 | 기준 5: 68–72% 플랫폼 사용률 | cvent.com/en/blog/events/event-statistics |
| Pavilion 2024 B2B SaaS Performance Metrics | 기준 3: SMB win rate 30–40% | joinpavilion.com |
| Optifai Win Rate by Deal Size 2025 | 기준 3: 회사 규모별 win rate | optif.ai |
| Cognism Buying Signals | 기준 4: 펀딩 후 2.5배, 리더십 교체 후 70% 예산 | cognism.com/blog/buying-signals |
| Zylo SaaS Trends 2026 | 기준 4: 헤드카운트 20%+ = 기술 도입 의향 | zylo.com/blog/saas-trends |
| Pipedrive Lead Scoring Guide | 기준 7: CEO/Director = 최고 점수 | pipedrive.com/en/blog/lead-scoring |
| Close.com SMB Sales | 기준 7: SMB CEO = 직접 의사결정 | close.com/blog/smb-sales |
| HBR "Making the Consensus Sale" | 기준 7: B2B 평균 5.4명 서명 | hbr.org/2015/03/making-the-consensus-sale |
| Belkins LinkedIn Outreach Study 2025 | 기준 7: C-suite 응답률 6.98% | belkins.io/blog/linkedin-outreach-study |
| Databox YouTube Statistics 2024 | YouTube: 200뷰 = 상위 30% | databox.com |
| HubSpot (13,500개 고객사) | Blog: 월 16개 = 4.5배 리드 (일반 B2B) | hubspot.com |
| IBISWorld Travel Agencies 2026 | 기준 3: 미국 여행사 규모 분포 | ibisworld.com |
