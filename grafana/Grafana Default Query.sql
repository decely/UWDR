SELECT * from main.dm_weather_data_distributed dm
join allrp.ds_dim_owd dim on dm.owd_id = dim.owd_id
where owd_name = 'OpenWeatherData'