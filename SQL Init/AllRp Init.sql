--Создание базы данных
CREATE DATABASE IF NOT EXISTS allrp on cluster 'all-replicated';


--Создание таблиц

--Таблица операторов погодных данных
CREATE TABLE IF NOT EXISTS allrp.ds_dim_owd ON cluster 'all-replicated'
(
	owd_id UUID,
	owd_name String,
	owd_short_name String,
	api String,
	create_dttm DateTime
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_owd_v2', '{replica}')
ORDER BY owd_id;
--Заполнение операторов
INSERT INTO allrp.ds_dim_owd
VALUES
(generateUUIDv4(), 'OpenWeatherMap', 'OWM', '9d0b56c67c3632e0a22741c5651aac5d', now()),
(generateUUIDv4(), 'WeatherApi', 'WA', 'e1a7a445d0bb4648a3d132511242304', now());


--Таблица распределенных по колонкам погодных данных
CREATE TABLE IF NOT EXISTS allrp.ds_dim_weather_data on cluster 'all-replicated'
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
	upload_dttm DateTime
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id)
TTL upload_dttm + INTERVAL 6 MONTH;


--Буферная таблица переведенных погодных данных DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_buffer_translated_weather_data on cluster 'all-replicated'
(
	id UUID,
	owd_id UUID,
	lang String,
	city String,
	wind_direction String,
	general_condition String
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_buffer_translated_weather_data_v2', '{replica}')
ORDER BY (id, owd_id);


--Таблица переведенных погодных данных DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_dim_translated_weather_data on cluster 'all-replicated'
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
	translate_dttm DateTime,
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_translated_weather_data_v2', '{replica}')
ORDER BY (id, ds_id, owd_id)
TTL translate_dttm + INTERVAL 6 MONTH;


--Таблица распределенных по колонкам данных прогноза
CREATE TABLE IF NOT EXISTS allrp.ds_dim_forecast_data on cluster 'all-replicated'
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
	upload_dttm DateTime
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_forecast_data_v2', '{replica}')
ORDER BY (id, divide_id, ds_id, owd_id)
TTL upload_dttm + INTERVAL 6 MONTH;


--Буферная таблица переведенных данных прогноза DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_buffer_translated_forecast_data on cluster 'all-replicated'
(
	id UUID,
	divide_id UUID,
	owd_id UUID,
	lang String,
	city String,
	wind_direction String,
	general_condition String
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_buffer_translated_forecast_data_v2', '{replica}')
ORDER BY (id, divide_id, owd_id);


--Таблица переведенных данных прогноза DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_dim_translated_forecast_data on cluster 'all-replicated'
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
	translate_dttm DateTime,
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_translated_forecast_data_v2', '{replica}')
ORDER BY (id, divide_id, ds_id, owd_id)
TTL translate_dttm + INTERVAL 6 MONTH;


--Таблица перевода погодных данных
CREATE TABLE IF NOT EXISTS allrp.ds_dim_trans on cluster 'all-replicated'(
    origin String,
    ru String,
    fr String
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_trans', '{replica}')
ORDER BY (origin)


--Словари

--Словарь перевода погодных данных
CREATE DICTIONARY if not exists allrp.dic_ds_dim_trans ON CLUSTER 'all-replicated'
(
    origin String,
    ru String,
    fr String
)
PRIMARY KEY origin
SOURCE (CLICKHOUSE(db 'allrp' TABLE 'ds_dim_trans'))
LIFETIME(MIN 3500 MAX 3600)
LAYOUT(COMPLEX_KEY_SPARSE_HASHED(PREALLOCATE 1));
