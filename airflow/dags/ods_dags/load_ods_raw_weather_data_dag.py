import importlib
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from services.ods_services.load_ods_raw_weather import hello_world_py

logger = logging.getLogger('airflow.task')

dag_params = {
    'dag_id': 'load_ods_raw_weather_data_dag',
    'description': 'Даг загрузки сырых данных о погоде по текущему времени из API',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ods','raw','weather'],
}
    

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    hello_world = PythonOperator(
        task_id='hello_world',
        python_callable=hello_world_py,
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        hello_world >> \
        finish
