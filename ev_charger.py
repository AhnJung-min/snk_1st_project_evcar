# -*- coding: utf-8 -*-
"""
한국환경공단 전기차 충전소 정보 수집기 (공공데이터포털 OpenAPI)

getChargerInfo 오퍼레이션을 페이지 단위로 호출해 충전소/충전기 정보를
위도·경도 포함하여 CSV/JSON 으로 저장한다. 외부 의존성은 requests 뿐.

사용법:
    python ev_charger.py --key 발급키 --max-pages 3      # 앞 3페이지(테스트)
    python ev_charger.py --key 발급키                    # 전체 수집
    python ev_charger.py --key 발급키 --zcode 11         # 서울만 (시도코드)
    python ev_charger.py --key 발급키 --out seoul_ev     # 출력 파일 접두어
"""

import argparse
import csv
import json
import sys
import time
import urllib3
import xml.etree.ElementTree as ET

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo"
NUM_OF_ROWS = 9999  # 한 페이지 최대 행 수

# 응답 필드 → 한글 헤더(원하는 항목만 골라 CSV 컬럼 순서 지정)
FIELDS = {
    "statNm": "충전소명",
    "statId": "충전소ID",
    "chgerId": "충전기ID",
    "chgerType": "충전기타입",
    "addr": "주소",
    "addrDetail": "상세주소",
    "lat": "위도",
    "lng": "경도",
    "useTime": "이용가능시간",
    "busiNm": "운영기관명",
    "busiCall": "운영기관연락처",
    "output": "충전용량(kW)",
    "method": "충전방식",
    "stat": "충전기상태",
    "zcode": "지역코드",
    "zscode": "지역상세코드",
    "parkingFree": "주차무료",
    "limitYn": "이용제한",
    "statUpdDt": "상태갱신일시",
}


def fetch_page(session, key, page, zcode=None):
    params = {"serviceKey": key, "pageNo": page, "numOfRows": NUM_OF_ROWS}
    if zcode:
        params["zcode"] = zcode
    r = session.get(API_URL, params=params, timeout=30, verify=False)
    r.raise_for_status()
    root = ET.fromstring(r.content)

    code = root.findtext(".//resultCode")
    if code not in ("00", "0"):
        msg = root.findtext(".//resultMsg")
        raise RuntimeError(f"API 오류 resultCode={code} resultMsg={msg}")

    total = int(root.findtext(".//totalCount") or 0)
    items = []
    for it in root.findall(".//item"):
        row = {}
        for tag in FIELDS:
            val = it.findtext(tag)
            row[tag] = "" if val in (None, "null") else val.strip()
        items.append(row)
    return items, total


def scrape(key, max_pages=None, zcode=None, delay=0.3):
    session = requests.Session()
    all_rows = []
    page = 1
    total = None
    while True:
        if max_pages and page > max_pages:
            break
        try:
            items, total = fetch_page(session, key, page, zcode)
        except (requests.RequestException, RuntimeError, ET.ParseError) as e:
            print(f"[!] {page}페이지 실패: {e}", file=sys.stderr)
            break

        if not items:
            print(f"[i] {page}페이지 항목 없음 → 종료")
            break

        all_rows.extend(items)
        print(f"[+] {page}페이지: {len(items)}건 (누적 {len(all_rows)} / 전체 {total})")

        if len(all_rows) >= total:
            break
        page += 1
        time.sleep(delay)

    return all_rows


def save(rows, out_prefix):
    json_path, csv_path = f"{out_prefix}.json", f"{out_prefix}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS.values())                       # 한글 헤더
        for row in rows:
            writer.writerow([row.get(k, "") for k in FIELDS])

    print(f"\n저장 완료: {json_path}, {csv_path} (총 {len(rows)}건)")


def main():
    ap = argparse.ArgumentParser(description="전기차 충전소 정보 수집기")
    ap.add_argument("--key", required=True, help="공공데이터포털 인증키(서비스키)")
    ap.add_argument("--max-pages", type=int, default=None, help="최대 페이지 수(테스트용)")
    ap.add_argument("--zcode", default=None, help="시도코드 필터(예: 서울 11, 경기 41)")
    ap.add_argument("--out", default="ev_charger", help="출력 파일 접두어")
    ap.add_argument("--delay", type=float, default=0.3, help="페이지 간 대기 초")
    args = ap.parse_args()

    rows = scrape(args.key, args.max_pages, args.zcode, args.delay)
    if rows:
        save(rows, args.out)
    else:
        print("수집된 항목이 없습니다.", file=sys.stderr)


if __name__ == "__main__":
    main()
