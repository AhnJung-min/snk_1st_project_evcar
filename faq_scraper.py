# -*- coding: utf-8 -*-
"""
한국교통안전공단(TS) 일반분야 FAQ 스크래퍼.

대상 페이지:
  https://main.kotsa.or.kr/portal/bbs/faq_list.do?menuCode=04010100 (자주하는 질문)

서버 렌더링 게시판이라 페이지(pageNumb) 단위로 HTML을 받아
질문/답변/카테고리/수정일을 추출한다. 외부 의존성 없이
requests + 표준 라이브러리만 사용한다.

사용법:
    python faq_scraper.py                 # 전체 페이지 → faq.json, faq.csv 저장
    python faq_scraper.py --max-pages 3   # 앞 3페이지만
    python faq_scraper.py --out result    # result.json / result.csv 로 저장
"""

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib3
from urllib.parse import urlencode

import requests

# kotsa.or.kr 은 인증서 체인 문제로 verify=False 사용 → 관련 경고 끔
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://main.kotsa.or.kr/portal/bbs/faq_list.do"
DEFAULT_PARAMS = {
    "menuCode": "04010000",   # 일반분야 > 자주하는 질문(FAQ)
    "cateCode": "",
    "sechCdtn": "0",
    "sechKywd": "",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}

# 한 FAQ 항목(<li>)을 통째로 잡는다.
#   <a ... onclick="fnc_setSearchCnt('376')"> ... [카테고리]&nbsp;질문</a>
#   <div data-bbsBody="conts"> ... <pre>답변</pre> ... 마지막 수정일 2025-09-09 ...
ITEM_RE = re.compile(
    r"fnc_setSearchCnt\('(?P<id>\d+)'\)"              # 항목 고유 번호
    r".*?질문</span>\s*(?P<title>.*?)</a>"            # 질문 줄
    r".*?답변</span>\s*<pre>(?P<answer>.*?)</pre>"    # 답변 본문
    r"(?:.*?마지막 수정일\s*(?P<date>\d{4}-\d{2}-\d{2}))?",  # 수정일(없을 수 있음)
    re.DOTALL,
)

# 질문 앞머리의 [카테고리] 분리용
CATE_RE = re.compile(r"^\s*\[(?P<cate>[^\]]+)\]\s*(?P<q>.*)$", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str) -> str:
    """HTML 태그 제거 + 엔티티 디코드 + 공백 정리."""
    text = TAG_RE.sub("", text)
    text = html.unescape(text).replace("\xa0", " ")
    # <pre> 안의 줄바꿈은 살리되 양끝 공백/과도한 빈 줄만 정리
    lines = [ln.rstrip() for ln in text.splitlines()]
    text = "\n".join(lines).strip()
    return text


def parse_page(htmltext: str):
    """한 페이지 HTML에서 FAQ 항목 리스트를 추출한다."""
    items = []
    for m in ITEM_RE.finditer(htmltext):
        raw_title = clean(m.group("title"))
        cate, question = "", raw_title
        cm = CATE_RE.match(raw_title)
        if cm:
            cate = cm.group("cate").strip()
            question = cm.group("q").strip()
        items.append({
            "id": m.group("id"),
            "category": cate,
            "question": question,
            "answer": clean(m.group("answer")),
            "modified": m.group("date") or "",
        })
    return items


def fetch_page(session: requests.Session, page: int) -> str:
    params = dict(DEFAULT_PARAMS, pageNumb=str(page))
    url = f"{BASE_URL}?{urlencode(params)}"
    resp = session.get(url, headers=HEADERS, verify=False, timeout=20)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


def scrape(max_pages: int | None = None, delay: float = 0.5):
    session = requests.Session()
    all_items = []
    seen_ids = set()
    page = 1
    while True:
        if max_pages and page > max_pages:
            break
        try:
            htmltext = fetch_page(session, page)
        except requests.RequestException as e:
            print(f"[!] {page}페이지 요청 실패: {e}", file=sys.stderr)
            break

        items = parse_page(htmltext)
        if not items:
            print(f"[i] {page}페이지에 항목 없음 → 종료")
            break

        # 마지막 페이지 이후 같은 내용이 반복되면 중복 id로 감지하여 종료
        new_items = [it for it in items if it["id"] not in seen_ids]
        if not new_items:
            print(f"[i] {page}페이지 신규 항목 없음(중복) → 종료")
            break

        for it in new_items:
            seen_ids.add(it["id"])
        all_items.extend(new_items)
        print(f"[+] {page}페이지: {len(new_items)}건 (누적 {len(all_items)}건)")
        page += 1
        time.sleep(delay)

    return all_items


def save(items, out_prefix: str):
    json_path = f"{out_prefix}.json"
    csv_path = f"{out_prefix}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "category", "question", "answer", "modified"]
        )
        writer.writeheader()
        writer.writerows(items)

    print(f"\n저장 완료: {json_path}, {csv_path} (총 {len(items)}건)")


def main():
    ap = argparse.ArgumentParser(description="TS 일반분야 FAQ 스크래퍼")
    ap.add_argument("--max-pages", type=int, default=None, help="가져올 최대 페이지 수")
    ap.add_argument("--out", default="faq", help="출력 파일 접두어 (기본: faq)")
    ap.add_argument("--delay", type=float, default=0.5, help="페이지 간 대기 초")
    args = ap.parse_args()

    items = scrape(max_pages=args.max_pages, delay=args.delay)
    if items:
        save(items, args.out)
    else:
        print("수집된 항목이 없습니다.", file=sys.stderr)


if __name__ == "__main__":
    main()
