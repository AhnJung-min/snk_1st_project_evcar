# snk_1st_project_evcar

전기차/교통 인프라 공공데이터 수집 → MySQL 적재 → Streamlit 시각화 팀 프로젝트.
공용 데이터베이스 이름은 **`ev_infra`** 로 통일한다. 각 팀원은 자신이 수집한
데이터셋을 같은 DB의 별도 테이블로 적재하고, 대시보드 페이지를 구성한다.

---

## 전체 흐름 한눈에 보기

```
[내 데이터 파일]          [ETL 스크립트]           [DB]              [대시보드]
data/내이름.csv   →   etl/load_내이름.py   →   ev_infra.테이블   →   app/pages/페이지.py
```

1. `data/` 폴더에 CSV(또는 JSON) 파일을 넣는다
2. `etl/load_<이름>.py` 를 작성해 DB에 적재한다
3. `sql/schema.sql` 에 내 테이블 DDL을 추가한다
4. `app/pages/<번호_이름>.py` 에 Streamlit 페이지를 추가한다

> **안정민(FAQ)** 은 API/스크래핑이 필요해서 `extract.py → transform.py → load.py` 로
> 3단계로 나뉘어 있지만, CSV를 이미 가지고 있는 팀원은 **`load_<이름>.py` 하나**만 작성하면 된다.

---

## 프로젝트 구조

```
project/
├── data/
│   ├── faq.json / faq.csv        # [안정민] FAQ 정제본 (예시)
│   └── <이름>.csv                # 팀원 데이터 파일 여기에 추가
│
├── etl/
│   ├── extract.py                # [안정민 전용] FAQ 웹 수집
│   ├── transform.py              # [안정민 전용] FAQ 정제
│   ├── load.py                   # [안정민 전용] faq 테이블 적재
│   └── load_<이름>.py            # 팀원 추가 → CSV 읽어서 DB 적재
│
├── sql/
│   └── schema.sql                # ev_infra DDL — 팀원 테이블도 여기에 추가
│
├── app/
│   ├── dashboard.py              # [안정민] FAQ 대시보드 (메인)
│   └── pages/
│       └── <번호_이름>.py        # 팀원 추가 → 본인 대시보드 페이지
│
├── .env.example                  # DB 접속 정보 템플릿
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 환경 세팅 (처음 한 번만)

```bash
# 1) 저장소 클론
git clone https://github.com/AhnJung-min/snk_1st_project_evcar.git
cd snk_1st_project_evcar

# 2) 의존성 설치
pip install -r requirements.txt

# 3) DB 접속 정보 설정  ← .env 는 절대 커밋하지 말 것
cp .env.example .env
# .env 를 열어 DB_HOST / DB_USER / DB_PASSWORD 입력

# 4) ev_infra DB + 테이블 생성
mysql -u root -p < sql/schema.sql
```

---

## 팀원 작업 순서 (CSV 파일이 있는 경우)

### Step 1 — 최신 코드 받기

```bash
git pull origin main
```

---

### Step 2 — 데이터 파일을 `data/` 에 넣기

CSV(또는 JSON) 파일을 `data/` 폴더에 복사한다.

```
data/
├── faq.json          ← 안정민 (건드리지 말 것)
└── 홍길동_ev.csv     ← 본인 파일 추가
```

**주의**: 용량이 크거나 민감한 원본 파일은 `_raw` 를 파일명에 붙이면 `.gitignore` 가 자동으로 제외한다.

```
data/홍길동_raw.csv   ← git 제외 (자동)
data/홍길동_ev.csv    ← git 포함 (정제본)
```

---

### Step 3 — 테이블 DDL 추가 (`sql/schema.sql`)

`schema.sql` 하단 "팀원 추가 영역"에 본인 테이블을 추가한다.

```sql
-- 예시
CREATE TABLE IF NOT EXISTS ev_charger (
    id          INT           NOT NULL,
    station_nm  VARCHAR(200)  NOT NULL  COMMENT '충전소명',
    addr        VARCHAR(300)  NULL      COMMENT '주소',
    lat         DECIMAL(10,7) NULL      COMMENT '위도',
    lng         DECIMAL(10,7) NULL      COMMENT '경도',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

추가한 뒤 본인 로컬 MySQL 에 반영한다.

```bash
mysql -u root -p < sql/schema.sql
```

---

### Step 4 — DB 적재 스크립트 작성 (`etl/load_<이름>.py`)

`data/` 의 CSV 를 읽어 DB 테이블에 넣는 스크립트를 작성한다.

```python
# etl/load_홍길동.py
import os, pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def get_engine():
    return create_engine(
        "mysql+pymysql://{u}:{p}@{h}:{port}/{db}?charset=utf8mb4".format(
            u=os.getenv("DB_USER", "root"),
            p=os.getenv("DB_PASSWORD", ""),
            h=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "3306"),
            db=os.getenv("DB_NAME", "ev_infra"),
        )
    )

def main():
    df = pd.read_csv(ROOT / "data" / "홍길동_ev.csv", encoding="utf-8-sig")

    # 컬럼명을 테이블 컬럼명으로 맞춰 주기
    df = df.rename(columns={"충전소명": "station_nm", "주소": "addr", "위도": "lat", "경도": "lng"})

    engine = get_engine()
    # if_exists="append" : 이미 데이터가 있으면 이어서 추가
    # if_exists="replace": 테이블을 날리고 다시 적재
    df.to_sql("ev_charger", con=engine, if_exists="append", index=False)
    print(f"적재 완료: ev_infra.ev_charger ({len(df)}건)")

if __name__ == "__main__":
    main()
```

작성 후 실행:

```bash
python etl/load_홍길동.py
```

---

### Step 5 — 대시보드 페이지 추가 (`app/pages/`)

`app/pages/` 폴더에 파일을 넣으면 Streamlit 사이드바에 자동으로 메뉴가 생긴다.
파일명 앞의 숫자가 메뉴 순서가 된다.

```
app/pages/
└── 2_충전소현황.py    ← 파일명 앞 숫자 = 사이드바 순서
```

```python
# app/pages/2_충전소현황.py
import os, pandas as pd, streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

st.set_page_config(page_title="충전소 현황", page_icon="⚡")
st.title("⚡ 전기차 충전소 현황")

@st.cache_data
def load_data():
    try:
        engine = create_engine(
            "mysql+pymysql://{u}:{p}@{h}:{port}/{db}?charset=utf8mb4".format(
                u=os.getenv("DB_USER","root"), p=os.getenv("DB_PASSWORD",""),
                h=os.getenv("DB_HOST","localhost"), port=os.getenv("DB_PORT","3306"),
                db=os.getenv("DB_NAME","ev_infra"),
            )
        )
        return pd.read_sql("SELECT * FROM ev_charger", engine)
    except Exception:
        # DB 없을 때 CSV 폴백
        return pd.read_csv(ROOT / "data" / "홍길동_ev.csv", encoding="utf-8-sig")

df = load_data()
st.dataframe(df)   # 여기서부터 본인 시각화 작성
```

---

### Step 6 — 커밋 & 푸시

**본인이 추가한 파일만** 명시적으로 add 한다.

```bash
git add data/홍길동_ev.csv
git add etl/load_홍길동.py
git add sql/schema.sql
git add app/pages/2_충전소현황.py

git commit -m "feat: [홍길동] 충전소 데이터 적재 및 대시보드 추가"

git pull origin main   # push 전에 최신화 (충돌 방지)
git push origin main
```

---

## 대시보드 실행

```bash
streamlit run app/dashboard.py
```

사이드바에서 본인 페이지로 이동할 수 있다.

---

## 담당 및 진행 현황

| 담당 | 데이터셋 | ETL 파일 | 테이블 | 페이지 | 진행 |
|---|---|---|---|---|---|
| 안정민 | 교통안전공단 FAQ | `extract.py` `transform.py` `load.py` | `faq` | `dashboard.py` | ✅ |
| (팀원) | (본인 데이터셋) | `load_<이름>.py` | (추가) | `pages/<번호_이름>.py` | - |

---

## 자주 묻는 것들

**Q. `.env` 를 커밋하면 안 되나요?**  
`.gitignore` 에 등록되어 있어 `git add .` 해도 자동으로 제외된다. DB 비밀번호가 GitHub에 올라가면 안 되니 절대 강제 추가하지 말 것.

**Q. DB 없이 대시보드를 볼 수 있나요?**  
DB 연결 실패 시 `data/` 폴더의 CSV/JSON 파일로 자동 폴백한다. 페이지 코드의 `except` 블록에 폴백 경로를 넣어두면 된다(위 Step 5 예시 참고).

**Q. `requirements.txt` 에 패키지를 추가해도 되나요?**  
필요한 패키지가 있으면 추가하고 같이 커밋한다. 버전은 특별한 이유가 없으면 고정하지 않는다.

**Q. 같은 파일을 동시에 수정하면 어떻게 되나요?**  
`git pull` 시 충돌이 발생한다. 이 README 의 작업 규칙(각자 별도 파일 추가)을 따르면 충돌이 거의 발생하지 않는다. `sql/schema.sql` 만 여러 명이 수정할 수 있으니 push 전 반드시 `git pull` 을 먼저 한다.
