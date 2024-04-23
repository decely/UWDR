import logging
from clickhouse_driver import Client

logger = logging.getLogger('airflow.task')

client = Client('clickhouse01')

def ch_run_query_empty(sql) -> None:
    """Функция для выполнения запроса без вывода данных"""
    
    sql = sql.rstrip()
    
    logger.info(f"Выполнение запроса: {sql}")
    
    client.execute(sql)
    
    logger.info("Запрос выполнен успешно")

def ch_run_query(sql) -> list:
    """Функция для выполнения запроса"""
    
    sql = sql.rstrip()
    
    logger.info(f"Выполнение запроса: {sql}")
    
    result = client.execute(sql)
    
    logger.info("Запрос выполнен успешно")
    
    return result