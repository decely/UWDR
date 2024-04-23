--Создание базы данных
CREATE DATABASE IF NOT EXISTS allrp on cluster 'all-replicated';


--Создание таблиц

--Таблица операторов погодных данных
CREATE TABLE IF NOT EXISTS allrp.ds_dim_owd ON cluster 'all-replicated'
(
	owd_id UUID, --Оператор погодных данных (weather api)
	owd_name String,
	owd_short_name String,
	create_dttm DateTime --now()
)
engine = ReplicatedMergeTree('/clickhouse/tables/all-replicated/ds_dim_owd', '{replica}')
ORDER BY owd_id;
--Заполнение операторов
INSERT INTO allrp.ds_dim_owd
VALUES
('dc8a9101-c5ef-47fc-bd13-f0e7ba4b3e32', 'OpenWeatherMap', 'OWM', now());