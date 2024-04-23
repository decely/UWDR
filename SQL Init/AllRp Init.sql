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

SELECT owd_name, owd_id, api from allrp.ds_dim_owd;