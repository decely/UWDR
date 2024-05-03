--Создание базы данных
CREATE DATABASE IF NOT EXISTS allrp on cluster 'all-replicated';


--Создание таблиц

--Таблица операторов погодных данных
CREATE TABLE IF NOT EXISTS allrp.ds_dim_owd ON cluster 'all-replicated'
(
	owd_id UUID, --Оператор погодных данных (weather api)
	owd_name String,
	owd_short_name String,
	api String,
	create_dttm DateTime --now()
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_owd', '{replica}')
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
	owd_id UUID,
	city String,
	temp Nullable(Float64), --В градусах по цельсию
	wind_speed Nullable(Float64), --Метры в секунду
	wind_direction String, --Юг, Север, Запад, Восток, Юго-Запад и т.д.
	atmospheric_pressure Nullable(Int), -- в мм ртутного столба
	humidity Nullable(Int), -- Влажность
	cloud_level Nullable(Int), -- Облачность в процентах
	general_condition String, -- Общее состояние (облачно, дождливо и т.д.)
	create_dttm DateTime, --из предыдущей таблицы
	upload_dttm DateTime --now()
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/all-replicated/ds_dim_weather_data', '{replica}')
ORDER BY (id, owd_id)
TTL upload_dttm + INTERVAL 6 MONTH;


--Буферная таблица переведенных даных DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_buffer_translated_weather_data on cluster 'all-replicated'
(
	id UUID,
	owd_id UUID,
	lang String,
	city String,
	wind_direction String,
	general_condition String
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/all-replicated/ds_buffer_translated_weather_data', '{replica}')
ORDER BY (id, owd_id);


--Таблица переведенных данных DS слоя
CREATE TABLE IF NOT EXISTS allrp.ds_dim_translated_weather_data on cluster 'all-replicated'
(
	id UUID,
	owd_id UUID,
	city String,
	temp Nullable(Float64), --В градусах по цельсию
	wind_speed Nullable(Float64), --Метры в секунду
	wind_direction String, --Юг, Север, Запад, Восток, Юго-Запад и т.д.
	atmospheric_pressure Nullable(Int), -- в мм ртутного столба
	humidity Nullable(Int), -- Влажность
	cloud_level Nullable(Int), -- Облачность в процентах
	general_condition String, -- Общее состояние (облачно, дождливо и т.д.)
	create_dttm DateTime, --из предыдущей таблицы
	upload_dttm DateTime, --из предыдущей таблицы
	translate_dttm DateTime, --now()
	lang String
)
engine = ReplicatedMergeTree('/clickhouse/tabkes/all-replicated/ds_dim_translated_weather_data', '{replica}')
ORDER BY (id, owd_id)
TTL translate_dttm + INTERVAL 6 MONTH;