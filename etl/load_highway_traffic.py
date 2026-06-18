# -*- coding: utf-8 -*-
"""
load_highway_traffic.py — 고속도로 통행량 데이터 MySQL 최종 적재

불필요한 sigungu_id 컬럼을 완벽히 제거하고,
순수 통행 데이터 11개 항목만으로 테이블을 새로 구성하여 초고속 적재를 완료한다.
"""

import sys
import pandas as pd
from pathlib import Path

# 공용 모듈(common) import를 위해 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.db import get_engine

EXCEL_PATH = settings.DATA_DIR / "highway_traffic.xlsx"


def main():
    if not EXCEL_PATH.exists():
        print(f"❌ 엑셀 파일을 찾을 수 없습니다: {EXCEL_PATH}")
        return

    engine = get_engine()
    print("🚀 불필요한 컬럼 제거 - 고속도로 통행량 데이터 최종 적재를 시작합니다...")

    chunk_size = 10000
    total_inserted = 0

    # 1. 엑셀 파일 로드 및 순수 11개 컬럼만 정제
    with pd.ExcelFile(EXCEL_PATH) as xls:
        df = pd.read_excel(xls)

        try:
            db_df = pd.DataFrame({
                'entry_toll_code': df['입구영업소코드'].astype(str),
                'entry_toll_name': df['입구영업소'].astype(str),
                'entry_address': df['입구영업소_주소'].astype(str),
                'exit_toll_code': df['출구영업소코드'].astype(str),
                'exit_toll_name': df['출구영업소'].astype(str),
                'exit_address': df['출구영업소_주소'].astype(str),
                'direction': df['상하행_구분'].astype(str),
                'ev_count': df['구간전기차이용대수'].fillna(0).astype(int),
                'total_vehicle_count': df['구간전체이용대수'].fillna(0).astype(int),
                'distance': df['영업소간거리'].fillna(0).astype(int),
                'exit_enter_date': df['출구진출일자'].astype(str)
            })
        except KeyError as e:
            print(f"\n❌ [오류] 엑셀 파일에 {e} 항목이 없습니다.")
            return

        print(f"🎯 [매핑 완료] sigungu_id가 완벽히 제거된 11개 순수 컬럼 정제 성공!")
        print("데이터베이스(highway_traffic) 테이블을 동기화하고 밀어 넣는 중...")

        # 2. 첫 번째 청크를 넣을 때 테이블을 깨끗하게 새로 만듭니다 (if_exists='replace')
        # 이를 통해 기존에 꼬여있던 NOT NULL 제약조건을 완전히 날려버립니다.
        first_chunk = db_df.iloc[0:chunk_size]
        first_chunk.to_sql(
            name='highway_traffic',
            con=engine,
            if_exists='replace',  # ⭕ 기존 테이블 밀어버리고 11개 컬럼으로 깔끔하게 새로 생성!
            index=False,
            method='multi',
            chunksize=1000
        )
        total_inserted += len(first_chunk)
        print(f" 진행 중... {total_inserted}/{len(db_df)} 행 적재 완료 (테이블 갱신 완료)")

        # 3. 나머지 데이터들을 append 방식으로 이어서 쭉쭉 밀어 넣습니다.
        for i in range(chunk_size, len(db_df), chunk_size):
            chunk = db_df.iloc[i:i + chunk_size]
            chunk.to_sql(
                name='highway_traffic',
                con=engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            total_inserted += len(chunk)
            print(f" 진행 중... {total_inserted}/{len(db_df)} 행 적재 완료")

    print(f"\n🎉 대성공!!! 총 {total_inserted}건의 통행량 데이터가 MySQL에 완벽하게 적재되었습니다!")
    print("⚠️ 이제 공지사항 준수를 위해 해당 통행량 엑셀 파일도 삭제하거나 폴더 밖으로 치워주세요!")


# 확인용

## pull push 확인용
if __name__ == "__main__":
    main()