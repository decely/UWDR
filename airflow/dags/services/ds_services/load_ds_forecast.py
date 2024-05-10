import logging

from plugins.uwdr_hook import ch_run_query_empty, ch_run_query

logger = logging.getLogger('airflow.task')


def need_to_load_forecast_data() -> str:
    """Проверка на необходимость загружать данные прогноза"""

    sql = """
    SELECT
        id,
        divide_id,
        owd_id,
    FROM allsh.ods_raw_divided_forecast_data_distributed as ods
    prewhere (id, owd_id) not in(
        select id, divide_id, owd_id from allrp.ds_dim_forecast_data
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    """

    result = ch_run_query(
        sql=sql,
    )

    if len(result) != 0:
        logger.info("Необходима загрузка новых данных прогноза")
        return 'load_needed'
    else:
        logger.info("Данные прогноза актуальны, нет надобности в загрузке")
        return 'finish'


def load_forecast_data_from_ods_to_ds() -> None:
    """Загрузка данных прогноза из ODS слоя в DS"""

    sql = """
    INSERT INTO allrp.ds_dim_forecast_data(
        id,
        divide_id,
        ds_id,
        owd_id,
        city,
        temp,
        wind_speed,
        wind_direction,
        atmospheric_pressure,
        humidity,
        cloud_level,
        general_condition,
	    forecast_ddtm,
        create_dttm,
        upload_dttm
    )
    SELECT
        id,
        divide_id,
        generateUUIDv4() as ds_id,
        owd_id,
        ods.city,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractFloat(json_string,'main','temp'),
            owd_name = 'WeatherApi', JSONExtractFloat(json_string,'current','temp_c'),
            Null
        ) as temp,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractFloat(json_string,'wind','speed'),
            owd_name = 'WeatherApi', trunc((JSONExtractFloat(json_string,'current','wind_kph'))/3.6, 2),
            Null
        ) as wind_speed,
        multiIf(
            owd_name = 'OpenWeatherMap', multiIf(
                JSONExtractInt(json_string,'wind','deg') >= 345 OR JSONExtractInt(json_string,'wind','deg') <= 15,'North',
                JSONExtractInt(json_string,'wind','deg') > 15 AND JSONExtractInt(json_string,'wind','deg') < 75,'North-East',
                JSONExtractInt(json_string,'wind','deg') >= 75 AND JSONExtractInt(json_string,'wind','deg') <= 105,'East',
                JSONExtractInt(json_string,'wind','deg') > 105 AND JSONExtractInt(json_string,'wind','deg') < 165,'South-East',
                JSONExtractInt(json_string,'wind','deg') >= 165 AND JSONExtractInt(json_string,'wind','deg') <= 195,'South',
                JSONExtractInt(json_string,'wind','deg') > 195 AND JSONExtractInt(json_string,'wind','deg') < 255,'South-West',
                JSONExtractInt(json_string,'wind','deg') >= 255 AND JSONExtractInt(json_string,'wind','deg') <= 285,'West',
                JSONExtractInt(json_string,'wind','deg') > 285 AND JSONExtractInt(json_string,'wind','deg') < 345,'North-West',
                'unidentified'
            ),
            owd_name = 'WeatherApi', multiIf(
                JSONExtractInt(json_string,'current','wind_degree') >= 345 OR JSONExtractInt(json_string,'current','wind_degree') <= 15,'North',
                JSONExtractInt(json_string,'current','wind_degree') > 15 AND JSONExtractInt(json_string,'current','wind_degree') < 75,'North-East',
                JSONExtractInt(json_string,'current','wind_degree') >= 75 AND JSONExtractInt(json_string,'current','wind_degree') <= 105,'East',
                JSONExtractInt(json_string,'current','wind_degree') > 105 AND JSONExtractInt(json_string,'current','wind_degree') < 165,'South-East',
                JSONExtractInt(json_string,'current','wind_degree') >= 165 AND JSONExtractInt(json_string,'current','wind_degree') <= 195,'South',
                JSONExtractInt(json_string,'current','wind_degree') > 195 AND JSONExtractInt(json_string,'current','wind_degree') < 255,'South-West',
                JSONExtractInt(json_string,'current','wind_degree') >= 255 AND JSONExtractInt(json_string,'current','wind_degree') <= 285,'West',
                JSONExtractInt(json_string,'current','wind_degree') > 285 AND JSONExtractInt(json_string,'current','wind_degree') < 345,'North-West',
                'unidentified'
            ),
            'unidentified'
        ) as wind_direction, --Надо подумать как переделать
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractInt(json_string,'main','pressure'),
            owd_name = 'WeatherApi', JSONExtractInt(json_string,'current','pressure_mb'),
            Null
        ) as atmospheric_pressure,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractInt(json_string,'main','humidity'),
            owd_name = 'WeatherApi', JSONExtractInt(json_string,'current','humidity'),
            Null
        ) as humidity,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractInt(json_string,'clouds','all'),
            owd_name = 'WeatherApi', JSONExtractInt(json_string,'current','cloud'),
            Null
        ) as cloud_level,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractString(JSONExtractArrayRaw(json_string,'weather')[1], 'main'),
            owd_name = 'WeatherApi', JSONExtractString(json_string,'current','condition','text'),
            'unidentified'
        ) as general_condition,
        create_dttm,
        now() as upload_dttm
    FROM allsh.ods_raw_forecast_data_distributed as ods
    JOIN allrp.ds_dim_owd as dim on ods.owd_id = dim.owd_id
    prewhere (id, owd_id) not in(
        select id, owd_id from allrp.ds_dim_forecast_data
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    """

    ch_run_query_empty(
        sql=sql,
    )
