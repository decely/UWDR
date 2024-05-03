--Создание базы данных
CREATE DATABASE IF NOT EXISTS main on cluster 'main';

--Создание таблиц

--STG-Таблица готовых погодных данных
CREATE TABLE IF NOT EXISTS main.stg_dm_weather_data on cluster 'main'
(
	id UUID,
	ds_id UUID,
	owd_id UUID,
	city String,
	temp Nullable(Float64),
	wind_speed Nullable(Float64),
	wind_direction String,
	atmospheric_pressure Nullable(Int),
	humidity Nullable(Int),
	cloud_level Nullable(Int),
	general_condition String,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/{shard}/stg_dm_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS  main.stg_dm_weather_data_distributed ON cluster 'main'
AS main.stg_dm_weather_data
ENGINE = Distributed('main', main, stg_dm_weather_data, rand());

CREATE TABLE IF NOT EXISTS main.dm_weather_data on cluster 'main'
(
	id UUID,
	ds_id UUID,
	owd_id UUID,
	city String,
	temp Nullable(Float64),
	wind_speed Nullable(Float64),
	wind_direction String,
	atmospheric_pressure Nullable(Int),
	humidity Nullable(Int),
	cloud_level Nullable(Int),
	general_condition String,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/{shard}/dm_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS  main.dm_weather_data_distributed ON cluster 'main'
AS main.dm_weather_data
ENGINE = Distributed('main', main, dm_weather_data, rand());