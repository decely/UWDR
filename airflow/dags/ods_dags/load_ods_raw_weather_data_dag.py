import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from services.ods_services.load_ods_raw_weather import get_owd_api_and_id, load_raw_weather_data_by_api

logger = logging.getLogger('airflow.task')

dag_params = {
    'dag_id': 'load_ods_raw_weather_data_dag',
    'description': 'Даг загрузки сырых данных о погоде по текущему времени из API',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ods', 'raw', 'weather'],
}
    

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    get_owd_api_and_id = PythonOperator(
        task_id='get_owd_api_and_id',
        python_callable=get_owd_api_and_id,
        do_xcom_push=True,
    )

    load_raw_weather_data_by_api = PythonOperator(
        task_id='load_raw_weather_data_by_api',
        python_callable=load_raw_weather_data_by_api,
        do_xcom_push=True,
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        get_owd_api_and_id >> \
        load_raw_weather_data_by_api >> \
        finish
