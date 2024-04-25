import logging

from plugins.uwdr_hook import ch_run_query_empty, ch_run_query

logger = logging.getLogger('airflow.task')

def need_to_load_weather_data() -> str:
    """Проверка на необходимость загружать погодные данные"""

    sql = """
    SELECT
        id,
        owd_id,
    FROM allsh.ods_raw_weather_data_distributed as ods
    prewhere (id, owd_id) not in(
        select id, owd_id from allrp.ds_dim_weather_data
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    """

    result = ch_run_query(
        sql=sql,
    )

    if len(result) != 0:
        logger.info("Необходима загрузка новых погодных данных")
        return 'load_needed'
    else:
        logger.info("Погодные данные актуальны, нет надобности в загрузке")
        return 'finish'


def load_weather_data_from_ods_to_ds() -> None:
    """Загрузка погодных данных из ODS слоя в DS"""

    sql = """
    INSERT INTO allrp.ds_dim_weather_data(
        id,
        owd_id,
        city,
        temp,
        wind_speed,
        wind_direction,
        atmospheric_pressure,
        humidity,
        cloud_level,
        general_condition,
        create_dttm,
        upload_dttm
    )
    SELECT
        id,
        owd_id,
        multiIf(
            owd_name = 'OpenWeatherMap', JSONExtractString(json_string,'name'),
            owd_name = 'WeatherApi', JSONExtractString(json_string,'location','name'),
            'unidentified'
        ) as city,
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
                JSONExtractInt(json_string,'wind','deg') >= 345 OR JSONExtractInt(json_string,'wind','deg') <= 15,'N',
                JSONExtractInt(json_string,'wind','deg') > 15 AND JSONExtractInt(json_string,'wind','deg') < 75,'NE',
                JSONExtractInt(json_string,'wind','deg') >= 75 AND JSONExtractInt(json_string,'wind','deg') <= 105,'E',
                JSONExtractInt(json_string,'wind','deg') > 105 AND JSONExtractInt(json_string,'wind','deg') < 165,'SE',
                JSONExtractInt(json_string,'wind','deg') >= 165 AND JSONExtractInt(json_string,'wind','deg') <= 195,'S',
                JSONExtractInt(json_string,'wind','deg') > 195 AND JSONExtractInt(json_string,'wind','deg') < 255,'SW',
                JSONExtractInt(json_string,'wind','deg') >= 255 AND JSONExtractInt(json_string,'wind','deg') <= 285,'W',
                JSONExtractInt(json_string,'wind','deg') > 285 AND JSONExtractInt(json_string,'wind','deg') < 345,'NW',
                'unidentified'
            ),
            owd_name = 'WeatherApi', multiIf(
                JSONExtractInt(json_string,'current','wind_degree') >= 345 OR JSONExtractInt(json_string,'current','wind_degree') <= 15,'N',
                JSONExtractInt(json_string,'current','wind_degree') > 15 AND JSONExtractInt(json_string,'current','wind_degree') < 75,'NE',
                JSONExtractInt(json_string,'current','wind_degree') >= 75 AND JSONExtractInt(json_string,'current','wind_degree') <= 105,'E',
                JSONExtractInt(json_string,'current','wind_degree') > 105 AND JSONExtractInt(json_string,'current','wind_degree') < 165,'SE',
                JSONExtractInt(json_string,'current','wind_degree') >= 165 AND JSONExtractInt(json_string,'current','wind_degree') <= 195,'S',
                JSONExtractInt(json_string,'current','wind_degree') > 195 AND JSONExtractInt(json_string,'current','wind_degree') < 255,'SW',
                JSONExtractInt(json_string,'current','wind_degree') >= 255 AND JSONExtractInt(json_string,'current','wind_degree') <= 285,'W',
                JSONExtractInt(json_string,'current','wind_degree') > 285 AND JSONExtractInt(json_string,'current','wind_degree') < 345,'NW',
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
    FROM allsh.ods_raw_weather_data_distributed as ods
    JOIN allrp.ds_dim_owd as dim on ods.owd_id = dim.owd_id
    prewhere (id, owd_id) not in(
        select id, owd_id from allrp.ds_dim_weather_data
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    """

    ch_run_query_empty(
        sql=sql,
    )
