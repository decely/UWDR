import logging
import json
import requests
from typing import List

from plugins.uwdr_hook import ch_run_query, ch_run_query_empty

logger = logging.getLogger('airflow.task')


def get_owd_api_and_id() -> List:
    """Получение owd_name, owd_id и api из таблицы ds_dim_owd"""

    sql = """
    SELECT
        owd_name,
        owd_id::String,
        api
    from allrp.ds_dim_owd
    """

    result = ch_run_query(
        sql=sql,
    )

    for row in result:
        owd_name = row[0]
        owd_id = row[1]
        api = row[2]
        logger.info(f"Найден оператор погодных данных. Название: {owd_name}, UUID: {owd_id}, api: {api}")

    return result


def load_raw_weather_data_by_api(cities_list, api_url_list, **context) -> None:
    """Получение сырых погодных данных через API"""

    api_info = context['ti'].xcom_pull(task_ids='get_owd_api_and_id')

    for row in api_info:
        for city in cities_list:
            owd_name = row[0]
            owd_id = row[1]
            api = row[2]
            logger.info(f"Получение сырых погодных данных от оператора {owd_name}")

            url = api_url_list[owd_name] + f"{api}&q={city}"

            data = requests.get(url).json()
            json_string = json.dumps(data)

            logger.info(f"Сырые данные от оператора {owd_name} по городу {city} успешно получены. Загрузка данных...")

            sql = """
            insert into allsh.ods_raw_weather_data_distributed(
                id,
                owd_id,
                json_string,
                create_dttm
            )
            select
                generateUUIDv4(),
                '{owd_id}',
                '{json_string}',
                now()
            """.format(
                owd_id=owd_id,
                json_string=json_string,
            )

            ch_run_query_empty(
                sql=sql,
            )
