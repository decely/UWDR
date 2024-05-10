import logging

from plugins.uwdr_hook import ch_run_query, ch_run_query_empty

logger = logging.getLogger('airflow.task')


def need_to_divide_forecast_data() -> str:
    """Проверка на необходимость разделять данные прогноза"""

    sql = """
    SELECT
        id,
        owd_id,
    FROM allsh.ods_raw_forecast_data_distributed as ods
    prewhere (id, owd_id) not in(
        select id, owd_id from allsh.ods_raw_divided_forecast_data_distributed
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    SETTINGS distributed_product_mode = 'allow'
    """

    result = ch_run_query(
        sql=sql,
    )

    if len(result) != 0:
        logger.info("Необходима разделение новых данных прогноза")
        return 'load_needed'
    else:
        logger.info("Данные прогноза актуальны, нет надобности в загрузке")
        return 'finish'


def load_raw_divided_forecast_data() -> None:
    """Разделение данных прогноза в ODS слое"""

    sql = """
    INSERT INTO allsh.ods_raw_divided_forecast_data_distributed(
        id,
        divide_id,
        owd_id,
        city,
        json_string,
        create_dttm,
        divide_dttm
    )
    SELECT
        id,
        generateUUIDv4() AS divide_id,
        owd_id,
        city,
        json AS json_string,
        create_dttm,
        now() AS divide_dttm
    from(
        SELECT
            id,
            owd_id,
            JSONExtractString(json_string, 'city', 'name') AS city,
            arrayJoin(JSONExtractArrayRaw(json_string, 'list')) AS json,
            create_dttm
        FROM allsh.ods_raw_forecast_data_distributed ods
        join allrp.ds_dim_owd dim on ods.owd_id = dim.owd_id
        where owd_name = 'OpenWeatherMap'
        ORDER BY id
        UNION ALL
        SELECT
        id,
        owd_id,
        JSONExtractString(json_string, 'location', 'name') AS city,
        arrayJoin(JSONExtractArrayRaw(arrayJoin(JSONExtractArrayRaw(json_string,'forecast','forecastday')),'hour')) AS json,
        create_dttm
        FROM allsh.ods_raw_forecast_data_distributed ods
        join allrp.ds_dim_owd dim on ods.owd_id = dim.owd_id
        where owd_name = 'WeatherApi'
        ORDER BY id
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    AND (id, owd_id) not in(select id, owd_id from allsh.ods_raw_divided_forecast_data_distributed)
    SETTINGS distributed_product_mode = 'allow'
    """

    ch_run_query_empty(
        sql=sql,
    )
