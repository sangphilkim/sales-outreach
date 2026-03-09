# youtube_tools.py

## 개요

YouTube Data API v3를 사용하여 **특정 YouTube 채널의 통계 데이터**를 수집하는 도구입니다.
채널 URL에서 채널명을 추출하고, 총 영상 수, 구독자 수, 조회수, 좋아요 수를 가져옵니다.

---

## 의존성

| 항목 | 설명 |
|------|------|
| `googleapiclient.discovery` | Google API 클라이언트 |
| `YOUTUBE_API_KEY` | 환경변수 — YouTube Data API 키 |

---

## 함수

### `extract_channel_name(url)`

YouTube 채널 URL에서 `@` 뒤의 채널명을 추출합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `url` | str | YouTube 채널 URL |

**반환값:** 채널명 문자열 / 없으면 `None`

```python
extract_channel_name("https://youtube.com/@MyChannel")  # → "MyChannel"
```

---

### `get_channel_id_by_name(channel_name)`

채널명으로 YouTube 채널 ID를 검색합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `channel_name` | str | YouTube 채널명 |

**반환값:** 채널 ID 문자열

**예외:** 채널을 찾지 못하면 `ValueError` 발생

---

### `get_channel_videos_stats(channel_id)`

채널의 상세 통계를 수집합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `channel_id` | str | YouTube 채널 ID |

**반환값 (dict):**

| 키 | 설명 |
|----|------|
| `total_videos` | 총 영상 수 |
| `subscriber_count` | 구독자 수 |
| `last_15_videos` | 최근 15개 영상 목록 (제목, 설명, 업로드 날짜) |
| `average_views` | 전체 영상 평균 조회수 |
| `average_likes` | 전체 영상 평균 좋아요 수 |

**동작 방식:**
1. 채널 전체 통계 조회 (총 영상 수, 구독자 수)
2. 최근 15개 영상 상세 정보 조회
3. 모든 영상 ID 수집 (페이지네이션 처리, 50개씩)
4. 영상별 통계 수집 후 평균 계산

---

### `get_youtube_stats(channel_url)` *(메인 함수)*

채널 URL을 입력받아 포맷된 통계 문자열을 반환합니다.

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `channel_url` | str | YouTube 채널 URL |

**반환값:** 포맷된 통계 문자열

**출력 예시:**
```
Total Videos: 150
Number of Subscribers: 50000
Average Views: 3200.5
Average Likes: 120.3
Last 15 Videos:
- AI Marketing Tips (Published: 2024-12-01T10:00:00Z)
- How to Automate SEO (Published: 2024-11-15T09:00:00Z)
...
```

---

## 환경변수

| 변수명 | 필수 여부 | 설명 |
|--------|----------|------|
| `YOUTUBE_API_KEY` | ✅ 필수 | YouTube Data API v3 키 |

---

## 사용 예시

```python
from src.tools.youtube_tools import get_youtube_stats

stats = get_youtube_stats("https://youtube.com/@SomeCompanyChannel")
print(stats)
```

---

## 주의사항

- YouTube Data API는 일일 할당량(Quota)이 있습니다. 대량 사용 시 초과될 수 있습니다.
- 채널 영상이 많을수록 모든 영상 통계 수집에 시간이 오래 걸립니다.
- 채널 URL에 `@` 기호가 없으면 채널명 추출에 실패합니다.
