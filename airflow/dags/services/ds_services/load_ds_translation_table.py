import logging
import argostranslate.package
import argostranslate.translate

from airflow.models import Variable

from plugins.uwdr_hook import ch_run_query_empty, ch_run_query

logger = logging.getLogger('airflow.task')

langs = Variable.get(key='langs_list', deserialize_json=True)["langs"]


def need_to_update_translation_table() -> str:
    """Проверка необходимости обновления таблицы с переводом погодных данных"""

    sql = """
    SELECT origin FROM (
    SELECT DISTINCT
        city AS `origin`
    FROM allrp.ds_dim_weather_data
    UNION ALL
    SELECT DISTINCT
        wind_direction AS `origin`
    FROM allrp.ds_dim_weather_data
    UNION ALL
    SELECT DISTINCT
        general_condition AS `origin`
    FROM allrp.ds_dim_weather_data
    )
    WHERE origin NOT IN (
        SELECT origin FROM allrp.ds_dim_trans
    )
    """

    result = ch_run_query(
        sql=sql,
    )

    if len(result) != 0:
        logger.info("Необходим перевод новых слов")
        load = 'update_needed'
    else:
        logger.info("Словарь актуален, нет надобности в переводе")
        load = 'finish'

    return load


def update_translate_libraries_if_needed() -> None:
    """Проверка и обновление библиотек для перевода при необходимости"""

    for lang in langs:
        logger.info(f"Обновление библиотек для языка {lang}")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == 'en' and x.to_code == lang, available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())


def prepare_load_translate_table() -> str:
    """Подготовка к заполнению таблицы с переводом"""

    sql = """
    SELECT DISTINCT
    general_condition AS `origin`
    FROM allrp.ds_dim_weather_data
    WHERE origin NOT IN (
        SELECT origin FROM allrp.ds_dim_trans
    )
    order by origin
    """

    sql_result = ch_run_query(
        sql=sql,
    )
    row = len(sql_result)
    column = len(langs) + 1
    translate_result = []

    for y in range(0, column):
        translate_result.append([])
        for x in range(0, row):
            to_translate = sql_result[x][0]
            if y != 0:
                if "light" in to_translate.lower() and "Patchy" not in to_translate:
                    to_translate = to_translate.replace("light", "moderate")
                    to_translate = to_translate.replace("Light", "Moderate")
                if to_translate == 'Clouds':
                    to_translate = 'Cloudy'
                if "rain" not in to_translate:
                    to_translate = to_translate + ' weather'
                translate = argostranslate.translate.translate(to_translate, 'en', langs[y - 1])
                to_translate = translate[0].upper() + translate[1:].lower()
            translate_result[y].append(to_translate)

    values_sql = ''

    for x in range(0, row):
        if x == 0:
            values_sql = "\n\t("
        else:
            values_sql = values_sql + ",("
        for y in range(0, column):
            if y == 0:
                values_sql = values_sql + f"'{translate_result[y][x]}'"
            else:
                values_sql = values_sql + f", '{translate_result[y][x]}'"
        values_sql = values_sql + ")\n\t"

    values = values_sql

    sql = """
    SELECT origin FROM (
    SELECT DISTINCT
        wind_direction AS `origin`
    FROM allrp.ds_dim_weather_data
    UNION ALL
    SELECT DISTINCT
        city AS `origin`
    FROM allrp.ds_dim_weather_data
    )
    WHERE origin NOT IN (
        SELECT origin FROM allrp.ds_dim_trans
    )
    """

    sql_result = ch_run_query(
        sql=sql,
    )
    row = len(sql_result)
    column = len(langs) + 1
    translate_result = []

    for y in range(0, column):
        translate_result.append([])
        for x in range(0, row):
            to_translate = sql_result[x][0]
            if y != 0:
                translate = argostranslate.translate.translate(to_translate, 'en', langs[y - 1])
                to_translate = translate[0].upper() + translate[1:].lower()
            translate_result[y].append(to_translate)

    values_sql = ''

    for x in range(0, row):
        if values != '':
            values_sql = values_sql + ",("
        else:
            values_sql = "("
        for y in range(0, column):
            if y == 0:
                values_sql = values_sql + f"'{translate_result[y][x]}'"
            else:
                values_sql = values_sql + f", '{translate_result[y][x]}'"
        values_sql = values_sql + ")\n\t"

    values = values + values_sql

    return values


def load_translation_to_weather(**context) -> None:
    """Запись переведенных погодных данных в буферную таблицу"""

    insert_sql = context['ti'].xcom_pull(task_ids='prepare_load_translate_table')

    logger.info("Запись переведенных погодных данных в буферную таблицу...")

    insert_list = 'origin'

    for lang in langs:
        insert_list = insert_list + ', ' + lang

    sql = """
    INSERT INTO allrp.ds_dim_trans(
        {insert_list}
    )
    VALUES""".format(
        insert_list=insert_list
    ) + insert_sql

    ch_run_query_empty(
        sql=sql,
    )


def reload_translation_dict() -> None:
    """Перезагрузка словаря с переводом слов"""

    sql = """
    SYSTEM RELOAD DICTIONARY allrp.dic_ds_dim_trans;
    """

    ch_run_query_empty(
        sql=sql,
    )
