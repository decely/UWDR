from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.task_group import TaskGroup

from services.ds_services.load_ds_translated_weather import (
    need_to_translate_weather_data,
    translate_ds_weather_data,
    truncate_buffer_table,
    load_weather_data_to_buffer,
    load_from_buffer_to_ds,
)

dag_params = {
    'dag_id': 'load_ds_weather_translated_data_dag',
    'description': 'Даг перевода и загрузки переведенных данных в DS слое',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ds', 'translate', 'weather'],
}

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    need_to_translate_weather_data = BranchPythonOperator(
        task_id='need_to_translate_weather_data',
        python_callable=need_to_translate_weather_data,
    )

    load_needed = EmptyOperator(task_id='load_needed')

    with TaskGroup(group_id='load_translate_to_buffer', prefix_group_id=False) as load_buffer_group:

        translate_ds_weather_data = PythonOperator(
            task_id='translate_ds_weather_data',
            task_group=load_buffer_group,
            python_callable=translate_ds_weather_data,
            do_xcom_push=True,
        )

        truncate_buffer_table = PythonOperator(
            task_id='truncate_buffer_table',
            task_group=load_buffer_group,
            python_callable=truncate_buffer_table,
        )

        load_weather_data_to_buffer = PythonOperator(
            task_id='load_weather_data_to_buffer',
            task_group=load_buffer_group,
            python_callable=load_weather_data_to_buffer,
        )

        translate_ds_weather_data >> truncate_buffer_table >> load_weather_data_to_buffer

    load_from_buffer_to_ds = PythonOperator(
        task_id='load_from_buffer_to_ds',
        python_callable=load_from_buffer_to_ds,
    )

    finish = EmptyOperator(task_id='finish', trigger_rule='none_failed_min_one_success')

    start >> \
        need_to_translate_weather_data >> \
        finish

    need_to_translate_weather_data >> \
        load_needed >> \
        load_buffer_group >> \
        load_from_buffer_to_ds >> \
        finish
