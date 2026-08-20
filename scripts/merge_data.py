# 여행 시기 특성 | 여행 비용 지출 특성 | 숙박여행유형정보를 각각 하나의 파일로 만듦 (2025년 데이터만)

import pandas as pd
from pathlib import Path

RAW_DIR = Path('data/raw')
OUT_DIR = Path('data/processed')
YEAR = 2025

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


def print_monthly_counts(df, month_col, label):
    # 지정한 월 컬럼 기준으로 1~12월 데이터 개수와 전체 합계 출력
    counts = df[month_col].value_counts().sort_index()
    print(f"[{label}] 월별 데이터 개수 (시작일 기준, {YEAR}년)")

    for month in range(1, 13):
        print(f"{month:2d}월: {counts.get(month, 0)}건")

    print(f"합계: {len(df)}건")


def build_era(year):
    # "여행 시기 특성" 원본 CSV 파일들을 모두 읽어 하나로 합친 뒤 지정 연도에 해당하는 데이터만 필터링해서 반환
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
    era_year = era_all[era_all['TOUR_YEAR'] == year].copy()
    return era_year


def build_expndtr(era_year):
    # "여행 비용 지출 특성" 원본 CSV 파일들을 모두 읽어 하나로 합친 뒤 지정 연도에 해당하는 데이터만 필터링해서 반환
    files = list(EXPNDTR_DIR.glob('*.csv'))
    dfs = []

    for file in files:
        df = read_csv_safely(file)
        df['__batch'] = extract_bath_date(file.name)
        dfs.append(df)
    expndtr_all = pd.concat(dfs, ignore_index=True)
    ref = era_year[["RESPOND_ID", "__batch",
                    "TOUR_BEGIN_DE", "TOUR_MONTH"]].drop_duplicates()
    ref = ref.rename(columns={"TOUR_BEGIN_DE": "TOUR_BEGIN_DE_FROM_ERA"})
    expndtr_year = expndtr_all.merge(
        ref, on=["RESPOND_ID", "__batch"], how="inner")
    return expndtr_year


def build_ldgmnt(year):
    # "숙박 여행 유형 정보" 원본 CSV 파일들을 모두 읽어 하나로 합친 뒤 지정 연도에 해당하는 데이터만 필터링해서 반환
    files = list(LDGMNT_DIR.glob('*.csv'))
    dfs = [read_csv_safely(file) for file in files]
    ldgmnt_all = pd.concat(dfs, ignore_index=True)

    ldgmnt_all["EXAMIN_YM"] = ldgmnt_all["EXAMIN_YM"].astype(int)
    ldgmnt_all["YM_YEAR"] = ldgmnt_all["EXAMIN_YM"] // 100
    ldgmnt_all["YM_MONTH"] = ldgmnt_all["EXAMIN_YM"] % 100

    ldgmnt_year = ldgmnt_all[ldgmnt_all['YM_YEAR'] == year].copy()

    return ldgmnt_year


def build_era_expndtr(era_year, expndtr_year):
    # "여행 시기 특성"과 "여행 비용 지출 특성"을 RESPOND_ID + __batch 기준으로 합쳐서 하나의 데이터셋으로 반환
    expndtr_for_merge = expndtr_year.drop(
        columns=["TOUR_BEGIN_DE_FROM_ERA", "TOUR_MONTH"])

    era_expndtr = era_year.merge(
        expndtr_for_merge, on=["RESPOND_ID", "__batch"], how="inner")
    return era_expndtr


def main():
    # ERA, EXPNDTR, LDGMNT, ERA+EXPNDTR 통합본을 각각 만들고 2025년 데이터를 CSV 4개로 저장
    print("\n[ERA 병합 및 2025년 필터링]")
    era_year = build_era(YEAR)
    print_monthly_counts(era_year, "TOUR_MONTH", "여행 시기 특성 (ERA)")

    print("\n[EXPNDTR 병합 및 2025년 필터링]")
    expndtr_year = build_expndtr(era_year)
    print_monthly_counts(expndtr_year, "TOUR_MONTH", "여행 비용 지출 특성 (EXPNDTR)")

    print("\n[LDGMNT 병합 및 2025년 필터링]")
    ldgmnt_year = build_ldgmnt(YEAR)
    print_monthly_counts(ldgmnt_year, "YM_MONTH", "숙박여행유형정보 (LDGMNT)")

    print("\n[ERA + EXPNDTR 통합]")
    era_expndtr_year = build_era_expndtr(era_year, expndtr_year)
    print_monthly_counts(era_expndtr_year, "TOUR_MONTH",
                         "여행 시기+비용 지출 통합 (ERA+EXPNDTR)")

    era_out = era_year.drop(columns=["__batch", "TOUR_YEAR", "TOUR_MONTH"])
    expndtr_out = expndtr_year.drop(columns=["__batch", "TOUR_MONTH"])
    ldgmnt_out = ldgmnt_year.drop(columns=["YM_YEAR", "YM_MONTH"])
    era_expndtr_out = era_expndtr_year.drop(
        columns=["__batch", "TOUR_YEAR", "TOUR_MONTH"])

    # 최종 결과를 각각 CSV로 저장 (utf-8-sig: 엑셀에서 한글 깨짐 방지)
    era_out.to_csv(
        OUT_DIR / f"travel_timing_{YEAR}.csv", index=False, encoding="utf-8-sig")
    expndtr_out.to_csv(
        OUT_DIR / f"travel_expenditure_{YEAR}.csv", index=False, encoding="utf-8-sig")
    ldgmnt_out.to_csv(
        OUT_DIR / f"accommodation_type_{YEAR}.csv", index=False, encoding="utf-8-sig")
    era_expndtr_out.to_csv(
        OUT_DIR / f"travel_timing_expenditure_{YEAR}.csv", index=False, encoding="utf-8-sig")

    print(f"\n저장 완료: {OUT_DIR}/travel_timing_{YEAR}.csv")
    print(f"저장 완료: {OUT_DIR}/travel_expenditure_{YEAR}.csv")
    print(f"저장 완료: {OUT_DIR}/accommodation_type_{YEAR}.csv")
    print(f"저장 완료: {OUT_DIR}/travel_timing_expenditure_{YEAR}.csv")
    print('전체 저장 완료')


if __name__ == '__main__':
    main()
