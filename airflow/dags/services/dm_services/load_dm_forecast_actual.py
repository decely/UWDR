import logging

from plugins.uwdr_hook import ch_run_query_empty

logger = logging.getLogger('airflow.task')


def truncate_stg_forecast_actual_data_table() -> None:
    """Очистка STG таблицы для записи готовых данных"""

    sql = """
    truncate table if exists main.stg_dm_forecast_actual_data on cluster 'main' sync;
    """

    ch_run_query_empty(
        sql=sql,
    )


def load_stg_forecast_actual_data_table() -> None:
    """Загрузка готовых данных в STG таблицу"""

    sql = """
    INSERT INTO main.stg_dm_forecast_actual_data_distributed(
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
        forecast_dttm,
        create_dttm,
        upload_dttm,
        translate_dttm,
        lang
    )
    SELECT
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
        forecast_dttm,
        create_dttm,
        upload_dttm,
        null,
        'en'
    FROM allrp.ds_dim_forecast_actual_data
    UNION ALL
    SELECT
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
        forecast_dttm,
        create_dttm,
        upload_dttm,
        translate_dttm,
        lang
    FROM allrp.ds_dim_translated_forecast_actual_data
    """

    ch_run_query_empty(
        sql=sql,
    )


def exchange_stg_and_dm_table() -> None:
    """Смена названий STG и DM таблиц"""

    sql = """
    EXCHANGE TABLES main.stg_dm_forecast_actual_data
    and main.dm_forecast_actual_data on cluster 'main';
    """

    ch_run_query_empty(
        sql=sql,
    )
