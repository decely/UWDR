from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from services.dm_services.load_dm_weather import (
    truncate_stg_weather_data_table,
    load_stg_weather_data_table,
    exchange_stg_and_dm_table
)

dag_params = {
    'dag_id': 'load_dm_weather_data_dag',
    'description': 'Даг загрузки готовых данных о погоде по текущему времени из DS в DM слой',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['dm', 'weather'],
}


with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    truncate_stg_weather_data_table = PythonOperator(
        task_id='truncate_stg_weather_data_table',
        python_callable=truncate_stg_weather_data_table,
    )

    load_stg_weather_data_table = PythonOperator(
        task_id='load_stg_weather_data_table',
        python_callable=load_stg_weather_data_table,
    )

    exchange_stg_and_dm_table = PythonOperator(
        task_id='exchange_stg_and_dm_table',
        python_callable=exchange_stg_and_dm_table,
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        truncate_stg_weather_data_table >> \
        load_stg_weather_data_table >> \
        exchange_stg_and_dm_table >> \
        finish
