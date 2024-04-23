import logging
import requests

from plugins.uwdr_hook import ch_run_query

logger = logging.getLogger('airflow.task')

api = '9d0b56c67c3632e0a22741c5651aac5d'

type = 'weather'

city = 'Voronezh'

url = f"http://api.openweathermap.org/data/2.5/{type}?q={city}&appid={api}&units=metric"


def hello_world_py() -> None:
    """Тестовый код таски"""
    
    sql = """
    select version()
    """
    
    result = ch_run_query(
        sql = sql,
    )
    
    logger.info(f"Текущая версия ClickHouse: {result[0][0]},")
    
    res = requests.get(url)

    data = res.json()
    
    logger.info(f"Текущая погода в {city}: {data['weather'][0]['description']}")