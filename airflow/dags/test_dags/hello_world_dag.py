import importlib
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from services.test_services.hello_world import hello_world_py

logger = logging.getLogger('airflow.task')

dag_params = {
    'dag_id': 'hello_world_dag',
    'description': 'Тестовый даг',
    'schedule_interval': None,
    'start_date': datetime(2022, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['test'],
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
