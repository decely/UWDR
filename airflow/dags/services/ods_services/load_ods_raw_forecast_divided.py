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


def prepare_load_raw_divided_data(owd_mapping) -> str:
    """Подготовка подзапроса для разделения данных"""

    first_owd = True

    pre_sql = ''

    for owd in owd_mapping:

        if not first_owd:
            pre_sql = pre_sql + '\n\tUNION ALL\n\t'
            first_owd = False

        pre_sql = pre_sql + """
        SELECT
            id,
            owd_id,
            JSONExtractString(json_string, {owd[1]}) AS city,
            arrayJoin(JSONExtractArrayRaw({owd[2]})) AS json,
            create_dttm
        FROM allsh.ods_raw_forecast_data_distributed ods
        join allrp.ds_dim_owd dim on ods.owd_id = dim.owd_id
        where owd_name = {owd[0]}
        ORDER BY id
        """.format(
            owd=owd
        )

    return pre_sql


def load_raw_divided_forecast_data(**context) -> None:
    """Разделение данных прогноза в ODS слое"""

    pre_sql = context['ti'].xcom_pull(task_ids='prepare_load_raw_divided_data')

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
        {pre_sql}
    )
    WHERE JSONExtractString(json_string, 'error') = ''
    AND JSONExtractString(json_string, 'cod') in('200','')
    AND (id, owd_id) not in(select id, owd_id from allsh.ods_raw_divided_forecast_data_distributed)
    SETTINGS distributed_product_mode = 'allow'
    """.format(
        pre_sql=pre_sql
    )

    ch_run_query_empty(
        sql=sql,
    )
