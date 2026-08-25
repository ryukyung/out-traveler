# 컬럼 정의서 — jinkyeong 전처리 산출물

작성 2026-08-24 · 대상 파일: `data/cleaned/jinkyeong_cleaned.csv` (14,342행 × 52열), `data/cleaned/jinkyeong_signgu_long.csv` (14,532행 × 4열)
전처리 근거는 `docs/전처리_이해_노트_jinkyeong.md` 참고. 이 문서는 컬럼 하나하나가 뭔지만 다룸.

---

## A. 식별자·원본 메타 (7열)

| 컬럼 | 타입 | 설명 | 값 예시 / 범위 |
|---|---|---|---|
| `RESPOND_ID` | int | 응답자 고유번호. **주의**: 34개 ID(81행)에서 성별 불일치 발견 — 완전히 고유하다고 단정 금지, `id_suspect` 참고 | 정수 |
| `EXAMIN_BEGIN_DE` | int | 조사 주차 시작일(YYYYMMDD). 여행일과 다름 — 이 값이 클수록 회상지연이 길다는 뜻 | 예: 20251117 |
| `TOUR_CTPRVN_NM` | str | 여행 방문 시·도. x/y 중복 컬럼을 통합한 것(원래 `_x`) | 예: 강원도 |
| `TOUR_SIGNGU_NM` | str | 여행 방문 시군구. `'모름'`/`'구체적인 지역 모름'`은 NaN 처리됨(→`TOUR_SIGNGU_NM_unk` 참고). `'가평군/화성시'`처럼 다목적지 응답은 원본 문자열 그대로 남아있음 — 시군구 단위 분석은 `jinkyeong_signgu_long.csv` 사용 | 예: 속초시, NaN, 가평군/화성시 |
| `TOUR_BEGIN_DE` | int | **실제 여행 시작일**(YYYYMMDD). 분석 기준 날짜는 이 컬럼 | 2025-01-01~12-31 |
| `TOUR_PD_VALUE` | str | 숙박일수 구간. `'모름'`은 NaN 처리됨 → 숫자화한 게 `nights` | 1박 2일 ~ 6박 7일 이상, NaN |
| `TOUR_COM_NMPR_NM` | str | 동반인원 구간. `'모름'`은 NaN 처리됨 → 숫자화한 게 `party_size` | 혼자서 ~ 5명 이상, NaN |

## B. 동반자 유형 (6열) — 다중응답, 사실상 5번째까지만 쓸모 있음

| 컬럼 | 타입 | 채워진 행 수 | 설명 |
|---|---|---|---|
| `COM_ONE_TY` | str | 14,207 | 동반자 유형 1번째 선택지 (배우자/혼자서/친구/가족/직장동료/연인 중 하나) |
| `COM_TWO_TY` | str | 2,700 | 2번째 선택지 (다중응답이라 있는 사람만) |
| `COM_THREE_TY` | str | 130 | 3번째 선택지 |
| `COM_FOUR_TY` | str | 7 | 4번째 선택지 |
| `COM_FIVE_TY` | str | 2 | 5번째 선택지 |
| `COM_SIX_TY` | float | **0** | **완전히 비어있음.** 실질적으로 죽은 컬럼 — 분석에 쓰지 말 것 |

> H4처럼 "동반유형"을 변수로 쓰려면 `COM_ONE_TY`(대표 동반자 유형)만 쓰는 게 실용적. 다중응답 전체를 살리려면 원-핫 인코딩 필요(아직 안 함).

## C. 여행목적·인적정보 (7열) — 전부 원본, x/y 통합됨

| 컬럼 | 타입 | 결측 | 설명 |
|---|---|---|---|
| `TOUR_PURPS_NM` | str | 0건 | 여행 목적. 12개 범주(자연풍경감상/휴식/문화예술 등). **결측 없음 — 유일하게 100% 응답된 주관식성 문항** |
| `SEXDSTN_FLAG_CD` | str | 0건 | 성별. `M`/`F`. **같은 `RESPOND_ID`끼리 값이 다르면 `id_suspect` 참고** |
| `AGRDE_FLAG_NM` | str | 0건 | 연령대. 20대~60대 이상 |
| `MRRG_AT_NM` | str | 0건 | 혼인상태 |
| `CHLDRN_TY_NM` | str | 0건 | 자녀유형 |
| `OCCP_NM` | str | 0건 | 직업군 |
| `HSHLD_INCOME_DGREE_NM` | str | 3,694건(원본 기준) | 가구소득 구간. `'모름'`은 NaN 처리됨(`HSHLD_INCOME_DGREE_NM_unk` 참고) |

## D. 지출 원본 6종 + 총액 (7열) — 구간형 문자열, 블록결측(0 또는 7)

| 컬럼 | 타입 | 구간 | 결측(모름) |
|---|---|---|---|
| `TOUR_TOT_CT_VALUE` | str | 10만원 미만 ~ 40만원 이상 (5구간) | 2,639건 |
| `TOUR_LDGMNT_CT_VALUE` | str | 숙박비. 1만원 미만 ~ 10만원 이상 (6구간) | 2,639건 |
| `TOUR_FOOD_CT_VALUE` | str | 식비 | 2,639건 |
| `TOUR_TRNSPORT_CT_VALUE` | str | 교통비 | 2,639건 |
| `TOUR_SHOPNG_CT_VALUE` | str | 쇼핑비 | 2,639건 |
| `TOUR_ACTVTY_CT_VALUE` | str | 액티비티비 | 2,639건 |
| `TOUR_ETC_CT_VALUE` | str | 기타비용 | 2,639건 |

> 7개 전부 같은 2,639명이 한꺼번에 결측(블록결측). "숙박비만 모른다" 같은 부분결측은 0건 — 항목 합으로 총액 대체 불가능한 이유.

## E. 결측 플래그 `_unk` (11열) — bool, 전부 결측 없음(항상 True/False)

`TOUR_TOT_CT_VALUE_unk`, `TOUR_LDGMNT_CT_VALUE_unk`, `TOUR_FOOD_CT_VALUE_unk`, `TOUR_TRNSPORT_CT_VALUE_unk`, `TOUR_SHOPNG_CT_VALUE_unk`, `TOUR_ACTVTY_CT_VALUE_unk`, `TOUR_ETC_CT_VALUE_unk`, `TOUR_PD_VALUE_unk`, `TOUR_COM_NMPR_NM_unk`, `HSHLD_INCOME_DGREE_NM_unk`, `TOUR_SIGNGU_NM_unk`

같은 이름의 원본 컬럼이 `'모름'`(또는 `'구체적인 지역 모름'`)이었으면 `True`. **이 자체가 분석 대상**(젊을수록 지출 모름률 높음 등) — 절대 삭제하지 말 것.

## F. 파생변수 (7열) — H3 핵심 지표

| 컬럼 | 타입 | 계산식 | 비고 |
|---|---|---|---|
| `nights` | float | `TOUR_PD_VALUE` 매핑 (1~6) | 결측 144건(`'모름'`) |
| `party_size` | float | `TOUR_COM_NMPR_NM` 매핑 (1~5) | 결측 453건 |
| `bound_assumed` | bool | `nights==6` 또는 `party_size==5` (열린구간 하한 가정) | True 시 과대추정 가능성 있음 |
| `tot_cost_mid` | float | `TOUR_TOT_CT_VALUE` 구간 중간값 대입(5/15/25/35/45만원) | 45는 base case 가정치 |
| `topcoded` | bool | `TOUR_TOT_CT_VALUE == '40만원 이상'` | True 1,870건. 제주 66% 집중 |
| `cost_per_person_night` | float | `tot_cost_mid / (nights × party_size)` | **H3 핵심 지표.** 유효 11,255건. 중위 5.0만원 |
| `ppn_high` | bool | `cost_per_person_night > Q3+1.5×IQR`(16.33만원) | True 777건(유효값의 6.9%). 삭제 아님 |

## G. 데이터 품질 플래그 (4열) — 오늘 새로 발견한 이슈

| 컬럼 | 타입 | 설명 | 규모 | 적용 규칙 |
|---|---|---|---|---|
| `id_suspect` | bool | 같은 `RESPOND_ID`인데 성별이 응답마다 다른 경우 | True 81행 (34개 ID) | H1~H3 무관, **H4에서만** 포함/제외 비교 |
| `trip_dup_group` | bool | 같은 사람·같은 여행일·같은 시도가 2회 이상 응답된 그룹에 속함 | True 160행 (78그룹) | H1 집계 시 포함/제외 비교 |
| `trip_dup_rank` | float | 그룹 내 조사주차(`EXAMIN_BEGIN_DE`) 순위. 1이 회상지연 가장 짧음 | 1, 2, 3(그룹 크기만큼) | 대표값 선정용 |
| `trip_dup_keep` | bool | 중복 없거나, 중복 그룹의 대표(rank=1)면 `True` | True 14,260행 | **H1 대표 필터: `df[df.trip_dup_keep]`** |

## H. accommodation_type_2025.csv 병합 (3열) — 응답자 단위, 여행 단위 아님

| 컬럼 | 타입 | 설명 | 주의 |
|---|---|---|---|
| `indiv_travel_ratio` | float | 그 응답자가 연중 응답한 `DMSTC_TOUR_TY_VALUE` 중 `'개별 여행'` 비율(0~1) | **특정 여행에 대한 값이 아니라 그 사람 전체 평균.** 결측 59행 |
| `residence` | str | 그 응답자의 최빈 거주지(시·도) | 메인 데이터 `TOUR_CTPRVN_NM`(방문지)과 다름 — "거주지=방문지"면 로컬 여행 판별 가능 |
| `acc_unmatched` | bool | `accommodation_type_2025.csv`에 이 응답자가 아예 없음 | True 59행. `'모름'`과 다른 성격(문항결측 아니라 설문 자체 미참여) |

---

## I. `jinkyeong_signgu_long.csv` (별도 파일, 4열)

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `row_id` | int | `jinkyeong_cleaned.csv`의 행 인덱스(원본 기준). 이걸로 다시 조인 가능 |
| `TOUR_CTPRVN_NM` | str | 방문 시·도 |
| `TOUR_SIGNGU_NM` | str | 방문 시군구. **다목적지 응답이 `/` 기준으로 분해되어 있음** — `row_id`가 중복될 수 있음(같은 여행이 여러 시군구로 나뉨) |
| `weight` | float | `1/n` 가중치(n=그 `row_id`가 몇 개 시군구로 쪼개졌는지). 시군구 집계 시 단순 개수 대신 이 가중치로 합산할 것 |

**메인 파일(`jinkyeong_cleaned.csv`)과 절대 그냥 합치지 말 것** — 관측 단위가 다름(여행 1건 vs 시군구 1개). 시군구 세부 분석에만 이 파일 사용.

---

## 빠르게 참고할 것 — "이 컬럼 왜 있지?" 할 때

- 이름에 `_unk`가 붙어있다 → 원본이 `'모름'`이었다는 뜻, 그 자체가 정보
- `bool` 타입인데 이름이 `_suspect`/`_group`/`_high`/`topcoded`/`_assumed` 계열 → 삭제 대상이 아니라 **민감도 분석용 필터**, 조건문(`df[~df.xxx]`)으로만 쓸 것
- `_x`/`_y`가 남아있으면 → 이건 이미 통합됐어야 하는 컬럼, 만약 보인다면 통합 코드가 안 돌아간 것
