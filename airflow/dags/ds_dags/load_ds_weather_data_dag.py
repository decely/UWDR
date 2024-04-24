from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from services.ds_services.load_ds_weather import load_weather_data_from_ods_to_ds

dag_params = {
    'dag_id': 'load_ds_weather_data_dag',
    'description': 'Даг загрузки данных о погоде по текущему времени из ODS в DS слой',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ds', 'weather'],
}
    

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    #TODO Сделать проверку необходимости загрузки, разветвление если загрузка нужна

    load_weather_data_from_ods_to_ds = PythonOperator(
        task_id='load_weather_data_from_ods_to_ds',
        python_callable=load_weather_data_from_ods_to_ds,
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        load_weather_data_from_ods_to_ds >> \
        finish
