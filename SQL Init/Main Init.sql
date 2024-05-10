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
engine = ReplicatedMergeTree('/clickhouse/tables/{shard}/stg_dm_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS  main.stg_dm_weather_data_distributed ON cluster 'main'
AS main.stg_dm_weather_data
ENGINE = Distributed('main', main, stg_dm_weather_data, rand());


--Таблица готовых погодных данных
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
engine = ReplicatedMergeTree('/clickhouse/tables/{shard}/dm_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS main.dm_weather_data_distributed ON cluster 'main'
AS main.dm_weather_data
ENGINE = Distributed('main', main, dm_weather_data, rand());


--STG-Таблица готовых данных актуального прогноза
CREATE TABLE IF NOT EXISTS main.stg_dm_forecast_actual_data on cluster 'main'
(
	id UUID,
	divide_id UUID,
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
	forecast_dttm DateTime,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/stg_dm_forecast_actual_data_v2', '{replica}', create_dttm)
ORDER BY (owd_id, city, lang, forecast_dttm);
--Дистр таблица
CREATE TABLE IF NOT EXISTS  main.stg_dm_forecast_actual_data_distributed ON cluster 'main'
AS main.stg_dm_forecast_actual_data
ENGINE = Distributed('main', main, stg_dm_forecast_actual_data, rand());


--Таблица готовых данных актуального прогноза
CREATE TABLE IF NOT EXISTS main.dm_forecast_actual_data on cluster 'main'
(
	id UUID,
	divide_id UUID,
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
	forecast_dttm DateTime,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/dm_forecast_actual_data_v2', '{replica}', create_dttm)
ORDER BY (owd_id, city, lang, forecast_dttm);
--Дистр таблица
CREATE TABLE IF NOT EXISTS main.dm_forecast_actual_data_distributed ON cluster 'main'
AS main.dm_forecast_actual_data
ENGINE = Distributed('main', main, dm_forecast_actual_data, rand());


--STG-Таблица готовых данных прогноза за все время
CREATE TABLE IF NOT EXISTS main.stg_dm_forecast_all_data on cluster 'main'
(
	id UUID,
	divide_id UUID,
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
	forecast_diff Int,
	forecast_dttm DateTime,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tables/{shard}/stg_dm_forecast_all_data_v2', '{replica}')
ORDER BY (id, divide_id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS  main.stg_dm_forecast_all_data_distributed ON cluster 'main'
AS main.stg_dm_forecast_all_data
ENGINE = Distributed('main', main, stg_dm_forecast_all_data, rand());


--Таблица готовых данных прогноза за все время
CREATE TABLE IF NOT EXISTS main.dm_forecast_all_data on cluster 'main'
(
	id UUID,
	divide_id UUID,
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
	forecast_diff Int,
	forecast_dttm DateTime,
	create_dttm DateTime,
	upload_dttm DateTime,
	translate_dttm Nullable(DateTime),
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tables/{shard}/dm_forecast_all_data_v2', '{replica}')
ORDER BY (id, divide_id, ds_id, owd_id);
--Дистр таблица
CREATE TABLE IF NOT EXISTS main.dm_forecast_all_data_distributed ON cluster 'main'
AS main.dm_forecast_all_data
ENGINE = Distributed('main', main, dm_forecast_all_data, rand());
