import logging
from typing import List
from googletrans import Translator

from plugins.uwdr_hook import ch_run_query_empty, ch_run_query

logger = logging.getLogger('airflow.task')

translator = Translator()

langs = ['ru','fr']

def need_to_translate_weather_data():
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
            logger.info("Необходима загрузка новых погодных данных")
            langs_needed.append(lang)
            load = 'load_needed'
        else:
            logger.info("Погодные данные актуальны, нет надобности в загрузке")
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


def translate_ds_weather_data() -> List:
    """Перевод погодных данных DS слоя и подготовка к загрузке в буферную таблицу"""

    insert_sql = []

    for lang in langs:

        logger.info(f"Получение непереведенных погодных данных по языку {lang} из DS слоя...")

        sql = """
        SELECT
            id,
            owd_id,
            '{lang}',
            city,
            wind_direction,
            general_condition,
        FROM allrp.ds_dim_weather_data as ods
        where (id, owd_id, '{lang}') not in(
            select id, owd_id, lang from allrp.ds_dim_translated_weather_data
        )
        """.format(
            lang=lang
        )

        sql_result = ch_run_query(
            sql=sql,
        )

        logger.info(f"Перевод погодных данных по языку {lang}...")

        row = len(sql_result)
        column = len(sql_result[0])
        translate_result = []

        for x in range(0, row):
            translate_result.append([])
            for y in range(0, column):
                if y <= 1:
                    translate_result[x].append(str(sql_result[x][y]))
                elif sql_result[x][y] == 'Clear' and lang == 'ru':
                    translate_result[x].append('Ясно')
                elif sql_result[x][y] == 'North-East' and lang == 'ru':
                    translate_result[x].append('Северо-Восток')
                elif y > 2:
                    translate = translator.translate(sql_result[x][y], src='en', dest=lang)
                    translate_result[x].append(translate.text)
                else:
                    translate_result[x].append(sql_result[x][y])

        logger.info(f"Формирование запроса записи переведенных погодных данных по языку {lang} в буферную таблицу...")

        values_sql = ''

        for x in range(0, row):
            if x == 0:
                values_sql = "\n\t("
            else:
                values_sql = values_sql + ",("
            for y in range(0, column):
                if y == 0:
                    values_sql = values_sql + f"'{translate_result[x][y]}'"
                else:
                    values_sql = values_sql + f", '{translate_result[x][y]}'"
            values_sql = values_sql + ")\n\t"

        insert_sql.append(values_sql)

    return insert_sql


def load_weather_data_to_buffer(**context) -> None:
    """Запись переведенных погодных данных в буферную таблицу"""

    insert_sql = context['ti'].xcom_pull(task_ids='translate_ds_weather_data')

    logger.info(f"Запись переведенных погодных данных в буферную таблицу...")

    for values_sql in insert_sql:
        sql = """
        INSERT INTO allrp.ds_buffer_translated_weather_data(
            id,
            owd_id,
            lang,
            city,
            wind_direction,
            general_condition
        )
        VALUES""" + values_sql

        ch_run_query_empty(
            sql=sql,
        )

def load_from_buffer_to_ds() -> None:

    logger.info(f"Запись переведенных погодных данных в основную таблицу...")

    sql = """
    INSERT INTO allrp.ds_dim_translated_weather_data(
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
        upload_dttm,
        translate_dttm,
        lang
    )
    SELECT
        dim.id,
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