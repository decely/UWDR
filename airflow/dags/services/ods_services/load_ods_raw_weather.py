import logging
import json
import requests
from typing import List

from plugins.uwdr_hook import ch_run_query, ch_run_query_empty

logger = logging.getLogger('airflow.task')

city = 'Voronezh'

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
        logger.info(f"Название оператора погодных данных: {row[0]}, UUID: {row[1]}, api: {row[2]}")

    return result


def load_raw_weather_data_by_api(**context) -> List:
    """Получение сырых погодных данных через API"""

    api_info = context['ti'].xcom_pull(task_ids='get_owd_api_and_id')

    for row in api_info:
        owd_name = row[0]
        owd_id = row[1]
        api = row[2]
        logger.info(f"Получение сырых погодных данных от оператора {owd_name}")

        if owd_name == 'OpenWeatherMap':
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"
            data = requests.get(url).json()
            json_string = json.dumps(data)

        logger.info(f"Сырые данные от оператора {owd_name} успешно получены. Загрузка данных...")

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