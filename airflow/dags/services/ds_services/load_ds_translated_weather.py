import logging
from typing import List

from airflow.models import Variable

from plugins.uwdr_hook import ch_run_query_empty, ch_run_query

logger = logging.getLogger('airflow.task')

langs = Variable.get(key='langs_list', deserialize_json=True)["langs"]


def need_to_translate_weather_data() -> str:
    """Проверка на необходимость переводить погодные данные"""

    load = 'finish'
    langs_needed = []

    for lang in langs:

        logger.info(f"Проверка переведенных погодных данных по языку {lang}...")

        sql = """
        SELECT
            id,
            owd_id,
        FROM allrp.ds_dim_weather_data as ods
        where (id, owd_id, '{lang}') not in(
            select id, owd_id, lang from allrp.ds_dim_translated_weather_data
        )
        """.format(
            lang=lang
        )

        result = ch_run_query(
            sql=sql,
        )

        if len(result) != 0:
            logger.info("Необходим перевод новых погодных данных")
            langs_needed.append(lang)
            load = 'load_needed'
        else:
            logger.info("Погодные данные актуальны, нет надобности в переводе")
            load = 'finish'

    return load


def truncate_buffer_table() -> None:
    """Очистка буферной таблицы для записи переведенных данных"""

    sql = """
    truncate table if exists allrp.ds_buffer_translated_weather_data on cluster 'all-replicated' sync;
    """

    ch_run_query_empty(
        sql=sql,
    )


def load_weather_data_to_buffer() -> None:
    """Запись переведенных погодных данных в буферную таблицу"""

    logger.info("Запись переведенных погодных данных в буферную таблицу...")

    for lang in langs:
        sql = """
        INSERT INTO allrp.ds_buffer_translated_weather_data(
            id,
            owd_id,
            lang,
            city,
            wind_direction,
            general_condition
        )
        SELECT
            id,
            owd_id,
            '{lang}',
            dictGetOrNull('allrp.dic_ds_dim_ord', '{lang}', city) AS city,
            dictGetOrNull('allrp.dic_ds_dim_ord', '{lang}', wind_direction) AS wind_direction,
            dictGetOrNull('allrp.dic_ds_dim_ord', '{lang}', general_condition) AS general_condition
        FROM allrp.ds_dim_weather_data as ods
        where (id, owd_id, '{lang}') not in(
            select id, owd_id, lang from allrp.ds_dim_translated_weather_data
        )""".format(
            lang = lang
        )

        ch_run_query_empty(
            sql=sql,
        )


def load_from_buffer_to_ds() -> None:

    logger.info("Запись переведенных погодных данных в основную таблицу...")

    sql = """
    INSERT INTO allrp.ds_dim_translated_weather_data(
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
        upload_dttm,
        translate_dttm,
        lang
    )
    SELECT
        dim.id,
        generateUUIDv4() as ds_id,
        dim.owd_id,
        buff.city,
        dim.temp,
        dim.wind_speed,
        buff.wind_direction,
        dim.atmospheric_pressure,
        dim.humidity,
        dim.cloud_level,
        buff.general_condition,
        dim.create_dttm,
        dim.upload_dttm,
        now() AS translate_dttm,
        buff.lang
    FROM allrp.ds_buffer_translated_weather_data buff
    INNER JOIN allrp.ds_dim_weather_data dim ON (dim.id, dim.owd_id) = (buff.id, buff.owd_id)
    """

    ch_run_query_empty(
        sql=sql,
    )
