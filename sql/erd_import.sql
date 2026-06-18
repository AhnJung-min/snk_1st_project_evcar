-- ============================================================
--  ERDCloud Import 전용 DDL  (논리형 한글 / 물리형 영문 동시 생성)
--  ERDCloud → Import → SQL(DDL) 에 아래 전체 붙여넣기
-- ============================================================

-- =====================  물리형 (영문)  =====================

CREATE TABLE `faq` (
	`source`	VARCHAR(100)	NOT NULL	DEFAULT '한국교통안전공단',
	`id`	INT	NOT NULL	COMMENT '원본 FAQ 번호(출처별 고유)',
	`category`	VARCHAR(50)	NULL,
	`question`	VARCHAR(500)	NOT NULL,
	`answer`	TEXT	NULL,
	`modified`	DATE	NULL,
	`created_at`	TIMESTAMP	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `ev_fire_records` (
	`id`	INT	NOT NULL,
	`fire_year`	INT	NOT NULL,
	`fire_month`	INT	NOT NULL,
	`sido`	VARCHAR(50)	NOT NULL,
	`ignition_main_category`	VARCHAR(50)	NOT NULL,
	`ignition_sub_category`	VARCHAR(100)	NOT NULL,
	`vehicle_location`	VARCHAR(50)	NULL,
	`ground_level`	VARCHAR(20)	NULL,
	`vehicle_status`	VARCHAR(50)	NULL,
	`ignition_point`	VARCHAR(50)	NULL
);

CREATE TABLE `car_ev_status` (
	`id`	INT	NOT NULL,
	`base_month`	VARCHAR(7)	NOT NULL,
	`region`	VARCHAR(50)	NOT NULL,
	`total_cars`	INT	NOT NULL,
	`ev_cars`	INT	NOT NULL,
	`ev_ratio`	FLOAT	NOT NULL
);

CREATE TABLE `raw_ev_charger_daily` (
	`charge_start_date`	VARCHAR(50)	NULL,
	`station_name`	VARCHAR(150)	NULL,
	`address`	VARCHAR(255)	NULL,
	`charger_id`	VARCHAR(100)	NULL,
	`charger_type`	VARCHAR(100)	NULL,
	`charge_count`	VARCHAR(50)	NULL,
	`total_charge_kwh`	VARCHAR(50)	NULL,
	`total_charge_time`	VARCHAR(50)	NULL
);

CREATE TABLE `raw_highway_traffic` (
	`entry_toll_code`	VARCHAR(50)	NULL,
	`entry_toll_name`	VARCHAR(100)	NULL,
	`entry_address`	VARCHAR(255)	NULL,
	`exit_toll_code`	VARCHAR(50)	NULL,
	`exit_toll_name`	VARCHAR(100)	NULL,
	`exit_address`	VARCHAR(255)	NULL,
	`direction`	VARCHAR(20)	NULL,
	`exit_date`	VARCHAR(50)	NULL,
	`ev_count`	VARCHAR(50)	NULL,
	`total_vehicle_count`	VARCHAR(50)	NULL,
	`distance_km`	VARCHAR(50)	NULL
);

CREATE TABLE `ev_charger_geo` (
	`geo_id`	INT	NOT NULL,
	`station_name`	VARCHAR(150)	NOT NULL,
	`address`	VARCHAR(255)	NULL,
	`latitude`	DECIMAL(12, 8)	NULL,
	`longitude`	DECIMAL(12, 8)	NULL,
	`api_status`	VARCHAR(30)	NULL,
	`api_message`	VARCHAR(255)	NULL,
	`created_at`	TIMESTAMP	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `ev_charging_analysis` (
	`charging_id`	INT	NOT NULL,
	`charge_date`	DATE	NOT NULL,
	`station_name`	VARCHAR(150)	NULL,
	`address`	VARCHAR(255)	NULL,
	`charger_type`	VARCHAR(100)	NULL,
	`charge_count`	INT	NULL,
	`total_charge_kwh`	DECIMAL(14, 2)	NULL,
	`total_charge_time`	DECIMAL(14, 2)	NULL,
	`avg_charge_kwh`	DECIMAL(14, 2)	NULL,
	`avg_charge_time`	DECIMAL(14, 2)	NULL,
	`created_at`	TIMESTAMP	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `ev_traffic_analysis` (
	`traffic_id`	INT	NOT NULL,
	`traffic_date`	DATE	NOT NULL,
	`entry_toll_name`	VARCHAR(100)	NULL,
	`exit_toll_name`	VARCHAR(100)	NULL,
	`direction`	VARCHAR(20)	NULL,
	`section_name`	VARCHAR(255)	NULL,
	`ev_count`	INT	NULL,
	`total_vehicle_count`	INT	NULL,
	`ev_ratio`	DECIMAL(8, 4)	NULL,
	`distance_km`	DECIMAL(10, 2)	NULL,
	`created_at`	TIMESTAMP	NULL	DEFAULT CURRENT_TIMESTAMP
);

-- =====================  논리형 (한글)  =====================

CREATE TABLE `FAQ` (
	`출처사이트`	VARCHAR	NOT NULL,
	`FAQ번호`	INT	NOT NULL,
	`카테고리`	VARCHAR	NULL,
	`질문`	VARCHAR	NULL,
	`답변`	TEXT	NULL,
	`수정일`	DATE	NULL,
	`적재시각`	TIMESTAMP	NULL
);

CREATE TABLE `전기차화재현황` (
	`화재ID`	INT	NOT NULL,
	`화재발생연도`	INT	NULL,
	`화재발생월`	INT	NULL,
	`시도`	VARCHAR	NULL,
	`발화요인대분류`	VARCHAR	NULL,
	`발화요인소분류`	VARCHAR	NULL,
	`차량장소`	VARCHAR	NULL,
	`지상지하`	VARCHAR	NULL,
	`차량상태`	VARCHAR	NULL,
	`차량발화지점`	VARCHAR	NULL
);

CREATE TABLE `전기차비중현황` (
	`행ID`	INT	NOT NULL,
	`기준연월`	VARCHAR	NULL,
	`지역`	VARCHAR	NULL,
	`전체자동차수`	INT	NULL,
	`전기차수`	INT	NULL,
	`전기차비중`	FLOAT	NULL
);

CREATE TABLE `충전소일별원본` (
	`충전시작일`	VARCHAR	NULL,
	`충전소명`	VARCHAR	NULL,
	`주소`	VARCHAR	NULL,
	`충전기ID`	VARCHAR	NULL,
	`충전기타입`	VARCHAR	NULL,
	`충전건수`	VARCHAR	NULL,
	`충전용량합계`	VARCHAR	NULL,
	`충전시간합계`	VARCHAR	NULL
);

CREATE TABLE `고속도로통행원본` (
	`입구영업소코드`	VARCHAR	NULL,
	`입구영업소명`	VARCHAR	NULL,
	`입구주소`	VARCHAR	NULL,
	`출구영업소코드`	VARCHAR	NULL,
	`출구영업소명`	VARCHAR	NULL,
	`출구주소`	VARCHAR	NULL,
	`방향`	VARCHAR	NULL,
	`출차일자`	VARCHAR	NULL,
	`전기차통행량`	VARCHAR	NULL,
	`전체통행량`	VARCHAR	NULL,
	`통행거리km`	VARCHAR	NULL
);

CREATE TABLE `충전소좌표` (
	`좌표ID`	INT	NOT NULL,
	`충전소명`	VARCHAR	NOT NULL,
	`주소`	VARCHAR	NULL,
	`위도`	DECIMAL	NULL,
	`경도`	DECIMAL	NULL,
	`API상태`	VARCHAR	NULL,
	`API메시지`	VARCHAR	NULL,
	`적재시각`	TIMESTAMP	NULL
);

CREATE TABLE `충전분석` (
	`충전분석ID`	INT	NOT NULL,
	`충전일자`	DATE	NOT NULL,
	`충전소명`	VARCHAR	NULL,
	`주소`	VARCHAR	NULL,
	`충전기타입`	VARCHAR	NULL,
	`충전건수`	INT	NULL,
	`총충전용량kWh`	DECIMAL	NULL,
	`총충전시간`	DECIMAL	NULL,
	`평균충전용량kWh`	DECIMAL	NULL,
	`평균충전시간`	DECIMAL	NULL,
	`적재시각`	TIMESTAMP	NULL
);

CREATE TABLE `통행분석` (
	`통행분석ID`	INT	NOT NULL,
	`통행일자`	DATE	NOT NULL,
	`입구영업소명`	VARCHAR	NULL,
	`출구영업소명`	VARCHAR	NULL,
	`방향`	VARCHAR	NULL,
	`구간명`	VARCHAR	NULL,
	`전기차통행량`	INT	NULL,
	`전체통행량`	INT	NULL,
	`전기차이용비율`	DECIMAL	NULL,
	`통행거리km`	DECIMAL	NULL,
	`적재시각`	TIMESTAMP	NULL
);

-- =====================  PK (물리형)  =====================

ALTER TABLE `faq` ADD CONSTRAINT `PK_faq` PRIMARY KEY (
	`source`,
	`id`
);

ALTER TABLE `ev_fire_records` ADD CONSTRAINT `PK_ev_fire_records` PRIMARY KEY (
	`id`
);

ALTER TABLE `car_ev_status` ADD CONSTRAINT `PK_car_ev_status` PRIMARY KEY (
	`id`
);

ALTER TABLE `ev_charger_geo` ADD CONSTRAINT `PK_ev_charger_geo` PRIMARY KEY (
	`geo_id`
);

ALTER TABLE `ev_charger_geo` ADD CONSTRAINT `UQ_ev_charger_geo_station` UNIQUE (
	`station_name`
);

ALTER TABLE `ev_charging_analysis` ADD CONSTRAINT `PK_ev_charging_analysis` PRIMARY KEY (
	`charging_id`
);

ALTER TABLE `ev_traffic_analysis` ADD CONSTRAINT `PK_ev_traffic_analysis` PRIMARY KEY (
	`traffic_id`
);

-- =====================  PK (논리형)  =====================

ALTER TABLE `FAQ` ADD CONSTRAINT `PK_FAQ` PRIMARY KEY (
	`출처사이트`,
	`FAQ번호`
);

ALTER TABLE `전기차화재현황` ADD CONSTRAINT `PK_전기차화재현황` PRIMARY KEY (
	`화재ID`
);

ALTER TABLE `전기차비중현황` ADD CONSTRAINT `PK_전기차비중현황` PRIMARY KEY (
	`행ID`
);

ALTER TABLE `충전소좌표` ADD CONSTRAINT `PK_충전소좌표` PRIMARY KEY (
	`좌표ID`
);

ALTER TABLE `충전소좌표` ADD CONSTRAINT `UQ_충전소좌표_충전소명` UNIQUE (
	`충전소명`
);

ALTER TABLE `충전분석` ADD CONSTRAINT `PK_충전분석` PRIMARY KEY (
	`충전분석ID`
);

ALTER TABLE `통행분석` ADD CONSTRAINT `PK_통행분석` PRIMARY KEY (
	`통행분석ID`
);

-- =====================  FK (관계)  =====================

ALTER TABLE `ev_charging_analysis` ADD CONSTRAINT `FK_charging_geo` FOREIGN KEY (
	`station_name`
) REFERENCES `ev_charger_geo` (
	`station_name`
);

ALTER TABLE `충전분석` ADD CONSTRAINT `FK_충전분석_충전소좌표` FOREIGN KEY (
	`충전소명`
) REFERENCES `충전소좌표` (
	`충전소명`
);
