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


def load_weather_data_from_ods_to_ds(owd_mapping) -> None:
    """Загрузка погодных данных из ODS слоя в DS"""

    for owd in owd_mapping:

        sql = """
        INSERT INTO allrp.ds_dim_weather_data(
            id,
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
            create_dttm,
            upload_dttm
        )
        SELECT
            id,
            generateUUIDv4() as ds_id,
            owd_id,
            JSONExtractString(json_string, {owd[1]}) as city,
            JSONExtractFloat(json_string, {owd[2]}) as temp,
            JSONExtractFloat(json_string, {owd[3]}) as wind_speed,
            multiIf(
                JSONExtractInt(json_string, {owd[4]}) NOT BETWEEN 15 AND 345,'North',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 15 AND 74,'North-East',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 75 AND 104,'East',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 105 AND 164,'South-East',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 165 AND 194,'South',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 195 AND 254,'South-West',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 255 AND 284,'West',
                JSONExtractInt(json_string, {owd[4]}) BETWEEN 285 AND 345,'North-West',
                'unidentified'
            ) as wind_direction,
            JSONExtractInt(json_string, {owd[5]}) as atmospheric_pressure,
            JSONExtractInt(json_string, {owd[6]}) as humidity,
            JSONExtractInt(json_string,'{owd[7]}) as cloud_level,
            if(
                owd_name = 'OpenWeatherMap', JSONExtractString(JSONExtractArrayRaw(json_string, {owd[8]}),
                JSONExtractString(json_string, {owd[8]})
            ) as general_condition,
            create_dttm,
            now() as upload_dttm
        FROM allsh.ods_raw_weather_data_distributed as ods
        JOIN allrp.ds_dim_owd as dim on ods.owd_id = dim.owd_id
        prewhere (id, owd_id) not in(
            select id, owd_id from allrp.ds_dim_weather_data
        )
        AND owd_name = '{owd[0]}'
        WHERE JSONExtractString(json_string, 'error') = ''
        AND JSONExtractString(json_string, 'cod') in('200','')
        """

        ch_run_query_empty(
            sql=sql,
        )
