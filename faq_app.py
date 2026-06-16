# -*- coding: utf-8 -*-
"""
TS 일반분야 FAQ 검색 앱 (Streamlit)

- faq_scraper.py 가 저장한 faq.json 을 읽어 검색/표시한다.
- 키워드 기반 검색: 질문(제목) 또는 답변(내용)에 키워드 포함 여부로 필터링.
- 출력은 단순 표가 아니라 카드형 게시판 형태(expander) 로 보여준다.

실행:
    streamlit run faq_app.py
"""

import json
import re
from pathlib import Path

import streamlit as st

DATA_PATH = Path(__file__).with_name("faq.json")

st.set_page_config(page_title="TS FAQ 검색", page_icon="🚗", layout="wide")


# ----------------------------------------------------------------------------- 데이터
@st.cache_data
def load_faq():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def highlight(text: str, keyword: str) -> str:
    """검색어를 <mark> 로 강조. HTML 특수문자는 이스케이프."""
    safe = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    if not keyword:
        return safe.replace("\n", "<br>")
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    safe = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe)
    return safe.replace("\n", "<br>")


def match(item, keyword, scope, categories):
    if categories and item["category"] not in categories:
        return False
    if not keyword:
        return True
    kw = keyword.lower()
    in_q = kw in item["question"].lower()
    in_a = kw in item["answer"].lower()
    if scope == "제목":
        return in_q
    if scope == "내용":
        return in_a
    return in_q or in_a  # 제목+내용


# ----------------------------------------------------------------------------- 스타일
st.markdown(
    """
    <style>
      .faq-card-q { font-size: 1.02rem; font-weight: 600; line-height: 1.5; }
      .faq-cate {
        display:inline-block; padding:2px 10px; border-radius:12px;
        background:#eef4ff; color:#2563eb; font-size:0.78rem; font-weight:600;
        margin-right:8px;
      }
      .faq-meta { color:#888; font-size:0.78rem; }
      .faq-answer {
        background:#fafafa; border-left:3px solid #2563eb; border-radius:6px;
        padding:14px 16px; line-height:1.7; font-size:0.93rem; color:#1a1a2e;
      }
      .faq-answer *, .faq-card-q * { color:inherit; }
      mark {
        background:transparent; color:#d97706; font-weight:700;
        border-bottom:2px solid #fcd34d; padding:0; border-radius:0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------- 헤더
st.title("🚗 한국교통안전공단 FAQ 검색")
st.caption("일반분야 자주하는 질문(FAQ) · 제목 또는 내용에서 키워드를 검색하세요.")

data = load_faq()
if not data:
    st.error("faq.json 을 찾을 수 없습니다. 먼저 `python faq_scraper.py` 를 실행해 데이터를 수집하세요.")
    st.stop()

# ----------------------------------------------------------------------------- 검색 입력
all_categories = sorted({d["category"] for d in data if d["category"]})

with st.container():
    c1, c2 = st.columns([3, 1])
    with c1:
        keyword = st.text_input("🔎 검색어", placeholder="예: 자동차검사, 과태료, 유효기간 …")
    with c2:
        scope = st.radio("검색 범위", ["제목+내용", "제목", "내용"], horizontal=True)

    sel_categories = st.multiselect("카테고리 필터", all_categories, default=[])

# ----------------------------------------------------------------------------- 필터링
results = [d for d in data if match(d, keyword, scope, sel_categories)]

left, right = st.columns([1, 1])
left.markdown(f"**검색 결과: {len(results)}건** / 전체 {len(data)}건")
view = right.radio("보기", ["카드형", "슬라이드형"], horizontal=True, label_visibility="collapsed")

st.divider()

if not results:
    st.info("검색 결과가 없습니다. 다른 키워드나 카테고리로 시도해 보세요.")
    st.stop()


# ----------------------------------------------------------------------------- 렌더링
def render_card(item):
    q = highlight(item["question"], keyword)
    cate = item["category"] or "기타"
    date = item["modified"] or "-"
    header = f"[{cate}] {item['question']}"
    with st.expander(header):
        st.markdown(
            f"<span class='faq-cate'>{cate}</span>"
            f"<span class='faq-meta'>마지막 수정일 {date} · No.{item['id']}</span>"
            f"<div class='faq-card-q' style='margin-top:8px'>Q. {q}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='faq-answer'>A. {highlight(item['answer'], keyword)}</div>",
            unsafe_allow_html=True,
        )


if view == "카드형":
    PAGE_SIZE = 10
    total_pages = (len(results) - 1) // PAGE_SIZE + 1
    page = 1
    if total_pages > 1:
        page = st.number_input(
            "페이지", min_value=1, max_value=total_pages, value=1, step=1
        )
    start = (page - 1) * PAGE_SIZE
    for item in results[start:start + PAGE_SIZE]:
        render_card(item)
    if total_pages > 1:
        st.caption(f"{page} / {total_pages} 페이지")

else:  # 슬라이드형 — 한 번에 한 건씩, 이전/다음 이동
    if "slide_idx" not in st.session_state:
        st.session_state.slide_idx = 0
    # 검색 결과가 바뀌면 범위를 벗어날 수 있으므로 보정
    st.session_state.slide_idx = max(0, min(st.session_state.slide_idx, len(results) - 1))

    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("⬅ 이전", use_container_width=True, disabled=st.session_state.slide_idx == 0):
            st.session_state.slide_idx -= 1
    with nav3:
        if st.button("다음 ➡", use_container_width=True, disabled=st.session_state.slide_idx >= len(results) - 1):
            st.session_state.slide_idx += 1
    with nav2:
        st.markdown(
            f"<div style='text-align:center;color:#888'>"
            f"{st.session_state.slide_idx + 1} / {len(results)}</div>",
            unsafe_allow_html=True,
        )

    item = results[st.session_state.slide_idx]
    cate = item["category"] or "기타"
    date = item["modified"] or "-"
    st.markdown(
        f"<span class='faq-cate'>{cate}</span>"
        f"<span class='faq-meta'>마지막 수정일 {date} · No.{item['id']}</span>"
        f"<div class='faq-card-q' style='margin:10px 0 14px'>Q. {highlight(item['question'], keyword)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='faq-answer'>A. {highlight(item['answer'], keyword)}</div>",
        unsafe_allow_html=True,
    )
