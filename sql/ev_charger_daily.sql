-- sql/schema.sql
-- 기존 충전소 테이블이 혹시 이상하게 만들어져 있다면 그것만 지우고 새로 만듭니다.
DROP TABLE IF EXISTS ev_charger_daily;

CREATE TABLE ev_charger_daily (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    base_month VARCHAR(50) NOT NULL,       -- 충전시작일 (기준월)
    station_name VARCHAR(255) NOT NULL,   -- 충전소명
    address VARCHAR(255) NOT NULL,        -- 주소
    charger_id VARCHAR(50) NULL,          -- 충전기ID
    charger_type VARCHAR(100) NULL,       -- 충전기타입
    charge_count INT NULL,                 -- 충전건수
    total_charge_amt INT NULL,            -- 충전용량_합계
    total_charge_time INT NULL,           -- 충전시간_합계
    charge_date DATE NULL,                 -- 충전_DATE
    sigungu_id INT NOT NULL,               -- ⭕ 기존 sigungu 테이블과 연결할 연결고리!

    -- SQLite에서 외래키(상위 테이블 연결) 지정하는 문법
    FOREIGN KEY (sigungu_id) REFERENCES sigungu(sigungu_id)
);