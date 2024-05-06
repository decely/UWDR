--Создание базы данных
CREATE DATABASE IF NOT EXISTS allsh on cluster 'all-sharded';


--Создание таблиц

--Таблица сырых погодных данных (текущее время)
CREATE TABLE IF NOT EXISTS allsh.ods_raw_weather_data ON cluster 'main'
(
	id UUID,
	owd_id UUID,
	json_string String,
	create_dttm DateTime
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/{shard}/ods_raw_weather_data', '{replica}')
ORDER BY (id, owd_id)
TTL create_dttm + INTERVAL 3 MONTH;
--Дистр таблица
CREATE TABLE IF NOT EXISTS allsh.ods_raw_weather_data_distributed ON cluster 'main'
AS allsh.ods_raw_weather_data
ENGINE = Distributed('main', allsh, ods_raw_weather_data, rand());