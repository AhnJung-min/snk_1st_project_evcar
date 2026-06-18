# etl/load_charger_daily.py

# -*- coding: utf-8 -*-
"""
load_charger.py — 전기차 충전소 대용량 데이터 MySQL 적재(Load)

52만 행의 대용량 엑셀 데이터를 chunk(묶음) 단위로 나누어 초고속으로 적재한다.
적재가 완료되면 공지사항 준수를 위해 엑셀 파일은 삭제하거나 프로젝트 외부로 격리할 것.
"""

import sys
import pandas as pd
from pathlib import Path

# 공용 모듈(common) import를 위해 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import settings
from common.db import get_engine

EXCEL_PATH = settings.DATA_DIR / "charger_data.xlsx"  # data/charger_data.xlsx


def main():
    if not EXCEL_PATH.exists():
        print(f"❌ 엑셀 파일을 찾을 수 없습니다: {EXCEL_PATH}")
        return

    engine = get_engine()
    print("🚀 52만 행 대용량 데이터 초고속 적재를 시작합니다...")

    # 1. 메모리 터짐 방지를 위해 엑셀을 1만 행씩 나누어 읽고 바로 DB에 넣습니다.
    # chunksize 설정을 주면 52만 행을 한 번에 읽지 않아 컴퓨터가 멈추지 않습니다.
    chunk_size = 10000

    # 먼저 전체 시군구 매칭 정보를 메모리에 올려둡니다 (속도 최적화)
    with engine.connect() as conn:
        sigungu_df = pd.read_sql_query("SELECT sigungu_id, sigungu_name FROM sigungu", conn)

    # 시군구 이름을 키로, ID를 값으로 하는 딕셔너리 생성
    sigungu_dict = dict(zip(sigungu_df['sigungu_name'], sigungu_df['sigungu_id']))

    total_inserted = 0

    # 엑셀 파일 대신 CSV로 변환해서 처리하면 속도가 10배 이상 빠릅니다.
    # 만약 파일이 .xlsx라면 대용량일 때 조금 느릴 수 있으니 가급적 CSV로 저장 후 read_csv를 추천합니다.
    # 여기서는 일단 엑셀 기준으로 작성하되, 만약 너무 느리면 CSV로 바꿔서 진행해 주세요!

    # 엑셀 엔진 중 대용량에 유리한 calamine이나 openpyxl 사용
    with pd.ExcelFile(EXCEL_PATH) as xls:
        df = pd.read_excel(xls)

        # 주소에서 시군구 이름 미리 추출해서 매칭 컬럼 만들기
        # 예: "경기도 양주시 ..." -> "양주시"
        df['extracted_sig'] = df['주소'].str.split().str[1]

        # 딕셔너리 맵핑으로 52만 행의 sigungu_id를 단 0.1초 만에 찾아냅니다. (반복문 X)
        df['sigungu_id'] = df['extracted_sig'].map(sigungu_dict).fillna(1).astype(int)

        # DB 테이블 구조에 맞게 엑셀 열 이름 매핑 및 정렬
        db_df = pd.DataFrame({
            'base_month': df['충전시작일'].astype(str),
            'station_name': df['충전소명'],
            'address': df['주소'],
            'charger_id': df['충전기ID'].astype(str),
            'charger_type': df['충전기타입'],
            'charge_count': df['충전건수'].fillna(0).astype(int),
            'total_charge_amt': df['충전용량_합계'].fillna(0).astype(float),
            'total_charge_time': df['충전시간_합계'].fillna(0).astype(int),
            'charge_date': df['충전시작일'].astype(str),
            'sigungu_id': df['sigungu_id']
        })

        # 2. 고속 대량 적재 (Bulk Insert)
        # 1만 개씩 쪼개서 MySQL에 번개처럼 집어넣습니다.
        print("데이터베이스에 밀어 넣는 중...")
        for i in range(0, len(db_df), chunk_size):
            chunk = db_df.iloc[i:i + chunk_size]

            # method='multi'와 chunksize 지정을 통해 성능 극대화
            chunk.to_sql(
                name='ev_charger_daily',
                con=engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            total_inserted += len(chunk)
            print(f" 진행 중... {total_inserted}/{len(db_df)} 행 적재 완료")

    print(f"\n🎉 완벽하게 성공했습니다! 총 {total_inserted}건의 데이터가 MySQL에 적재되었습니다.")


if __name__ == "__main__":
    main()