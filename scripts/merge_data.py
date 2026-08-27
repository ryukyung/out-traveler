"""
 * 여행시기특성 | 여행비용지출특성 | 숙박여행유형정보를 각각 하나의 파일로 만듦
 * 연도를 리스트로 지정해 여러 연도를 한 번에 처리 가능 (확장 가능한 구조)
 *
 * [입력 폴더/파일]
 *   data/raw/travel_timing/*.csv        -> "여행 시기 특성" 원본 (여러 파일)
 *   data/raw/travel_expenditure/*.csv   -> "여행 비용 지출 특성" 원본 (여러 파일)
 *   data/raw/accommodation_type/*.csv   -> "숙박여행유형정보" 원본 (여러 파일)
 *
 * [출력 폴더/파일] (연도별로 각각 4개씩 생성됨, {year}는 --years로 지정한 연도)
 *   data/processed/travel_timing_{year}.csv               -> 여행 시기 특성
 *   data/processed/travel_expenditure_{year}.csv           -> 여행 비용 지출 특성
 *   data/processed/accommodation_type_{year}.csv           -> 숙박여행유형정보
 *   data/processed/travel_timing_expenditure_{year}.csv    -> 여행 시기 + 비용 지출 통합본
 *
 * [터미널 사용법]
 *   python scripts/merge_data.py --years 2025
 *   python scripts/merge_data.py --years 2025 2024
"""

import argparse
import pandas as pd
from pathlib import Path

RAW_DIR = Path('data/raw')
OUT_DIR = Path('data/processed')

ERA_DIR = RAW_DIR / "travel_timing"
EXPNDTR_DIR = RAW_DIR / "travel_expenditure"
LDGMNT_DIR = RAW_DIR / "accommodation_type"

ENCODINGS = ["utf-8-sig", "cp949", "euc-kr"]


def read_csv_safely(path):
    # 여러 인코딩을 순서대로 시도하며 CSV 파일을 안전하게 읽어들이는 함수
    last_err = None

    for enc in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
    raise last_err


def extract_bath_date(filename):
    # 파일명에서 마지막 '_' 뒤의 문자열을 추출 (원본 파일 구분을 위해)
    return Path(filename).stem.split('_')[-1]


def print_monthly_counts(df, month_col, label, year):
    # 지정한 월 컬럼 기준으로 1~12월 데이터 개수와 전체 합계 출력
    counts = df[month_col].value_counts().sort_index()
    print(f"[{label}] 월별 데이터 개수 (시작일 기준, {year}년)")

    for month in range(1, 13):
        print(f"{month:2d}월: {counts.get(month, 0)}건")

    print(f"합계: {len(df)}건")


# ---- 원본 파일 읽기는 연도와 무관하므로 캐싱해서 한 번만 수행 ----
_era_all_cache = None
_expndtr_all_cache = None
_ldgmnt_all_cache = None


def load_era_all():
    # "여행 시기 특성" 원본 CSV 전체를 한 번만 읽어 캐싱 후 반환
    global _era_all_cache
    if _era_all_cache is None:
        files = list(ERA_DIR.glob("*.csv"))
        dfs = []
        for file in files:
            df = read_csv_safely(file)
            df['__batch'] = extract_bath_date(file.name)
            dfs.append(df)
        era_all = pd.concat(dfs, ignore_index=True)
        era_all['TOUR_BEGIN_DE'] = era_all['TOUR_BEGIN_DE'].astype(int)
        era_all['TOUR_YEAR'] = era_all['TOUR_BEGIN_DE'] // 10000
        era_all['TOUR_MONTH'] = (era_all['TOUR_BEGIN_DE'] // 100) % 100
        _era_all_cache = era_all
    return _era_all_cache


def load_expndtr_all():
    # "여행 비용 지출 특성" 원본 CSV 전체를 한 번만 읽어 캐싱 후 반환
    global _expndtr_all_cache
    if _expndtr_all_cache is None:
        files = list(EXPNDTR_DIR.glob('*.csv'))
        dfs = []
        for file in files:
            df = read_csv_safely(file)
            df['__batch'] = extract_bath_date(file.name)
            dfs.append(df)
        _expndtr_all_cache = pd.concat(dfs, ignore_index=True)
    return _expndtr_all_cache


def load_ldgmnt_all():
    # "숙박여행유형정보" 원본 CSV 전체를 한 번만 읽어 캐싱 후 반환
    global _ldgmnt_all_cache
    if _ldgmnt_all_cache is None:
        files = list(LDGMNT_DIR.glob('*.csv'))
        dfs = [read_csv_safely(file) for file in files]
        ldgmnt_all = pd.concat(dfs, ignore_index=True)
        ldgmnt_all["EXAMIN_YM"] = ldgmnt_all["EXAMIN_YM"].astype(int)
        ldgmnt_all["YM_YEAR"] = ldgmnt_all["EXAMIN_YM"] // 100
        ldgmnt_all["YM_MONTH"] = ldgmnt_all["EXAMIN_YM"] % 100
        _ldgmnt_all_cache = ldgmnt_all
    return _ldgmnt_all_cache


# ---- 연도별 필터링 함수 (year를 인자로 받아 어떤 연도에도 재사용 가능) ----

def build_era(year):
    # 캐싱된 ERA 전체 데이터에서 지정 연도만 필터링해 반환
    era_all = load_era_all()
    return era_all[era_all['TOUR_YEAR'] == year].copy()


def build_expndtr(era_year, year):
    # EXPNDTR 전체 데이터를 해당 연도의 ERA 데이터와 매칭해 필터링 후 반환
    expndtr_all = load_expndtr_all()
    ref = era_year[["RESPOND_ID", "__batch",
                    "TOUR_BEGIN_DE", "TOUR_MONTH"]].drop_duplicates()
    ref = ref.rename(columns={"TOUR_BEGIN_DE": "TOUR_BEGIN_DE_FROM_ERA"})
    expndtr_year = expndtr_all.merge(
        ref, on=["RESPOND_ID", "__batch"], how="inner")
    return expndtr_year


def build_ldgmnt(year):
    # 캐싱된 LDGMNT 전체 데이터에서 지정 연도만 필터링해 반환
    ldgmnt_all = load_ldgmnt_all()
    return ldgmnt_all[ldgmnt_all['YM_YEAR'] == year].copy()


def build_era_expndtr(era_year, expndtr_year):
    # ERA와 EXPNDTR을 RESPOND_ID + __batch 기준으로 병합해 통합 데이터셋을 반환한다.
    expndtr_for_merge = expndtr_year.drop(
        columns=["TOUR_BEGIN_DE_FROM_ERA", "TOUR_MONTH"])
    era_expndtr = era_year.merge(
        expndtr_for_merge, on=["RESPOND_ID", "__batch"], how="inner")
    return era_expndtr


def process_year(year):
    # 지정한 한 연도에 대해 ERA/EXPNDTR/LDGMNT/통합본을 만들어 CSV 4개로 저장한다.
    print(f"\n{'='*50}")
    print(f"{year}년 처리 시작")
    print(f"{'='*50}")

    print(f"\n[ERA 병합 및 {year}년 필터링]")
    era_year = build_era(year)
    print_monthly_counts(era_year, "TOUR_MONTH", "여행 시기 특성 (ERA)", year)

    print(f"\n[EXPNDTR 병합 및 {year}년 필터링]")
    expndtr_year = build_expndtr(era_year, year)
    print_monthly_counts(expndtr_year, "TOUR_MONTH",
                         "여행 비용 지출 특성 (EXPNDTR)", year)

    print(f"\n[LDGMNT 병합 및 {year}년 필터링]")
    ldgmnt_year = build_ldgmnt(year)
    print_monthly_counts(ldgmnt_year, "YM_MONTH", "숙박여행유형정보 (LDGMNT)", year)

    print(f"\n[ERA + EXPNDTR 통합({year})]")
    era_expndtr_year = build_era_expndtr(era_year, expndtr_year)
    print_monthly_counts(era_expndtr_year, "TOUR_MONTH",
                         "여행 시기+비용 지출 통합 (ERA+EXPNDTR)", year)

    era_out = era_year.drop(columns=["__batch", "TOUR_YEAR", "TOUR_MONTH"])
    expndtr_out = expndtr_year.drop(columns=["__batch", "TOUR_MONTH"])
    ldgmnt_out = ldgmnt_year.drop(columns=["YM_YEAR", "YM_MONTH"])
    era_expndtr_out = era_expndtr_year.drop(
        columns=["__batch", "TOUR_YEAR", "TOUR_MONTH"])

    # 최종 결과를 각각 CSV로 저장 (utf-8-sig: 엑셀에서 한글 깨짐 방지)
    era_out.to_csv(
        OUT_DIR / f"travel_timing_{year}.csv", index=False, encoding="utf-8-sig")
    expndtr_out.to_csv(
        OUT_DIR / f"travel_expenditure_{year}.csv", index=False, encoding="utf-8-sig")
    ldgmnt_out.to_csv(
        OUT_DIR / f"accommodation_type_{year}.csv", index=False, encoding="utf-8-sig")
    era_expndtr_out.to_csv(
        OUT_DIR / f"travel_timing_expenditure_{year}.csv", index=False, encoding="utf-8-sig")

    print(f"\n저장 완료: {OUT_DIR}/travel_timing_{year}.csv")
    print(f"저장 완료: {OUT_DIR}/travel_expenditure_{year}.csv")
    print(f"저장 완료: {OUT_DIR}/accommodation_type_{year}.csv")
    print(f"저장 완료: {OUT_DIR}/travel_timing_expenditure_{year}.csv")


def main():
    # --years로 받은 연도 목록을 순회하며 process_year를 실행하는 진입점.
    parser = argparse.ArgumentParser(description="여행 관련 데이터셋을 연도별로 생성")
    parser.add_argument(
        "--years", type=int, nargs="+", required=True,
        help="처리할 연도 목록 (예: --years 2025 2024 2023)"
    )
    args = parser.parse_args()

    for year in args.years:
        process_year(year)

    print("\n전체 저장 완료")


if __name__ == '__main__':
    main()
