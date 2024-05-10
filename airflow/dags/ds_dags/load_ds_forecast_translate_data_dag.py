from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.task_group import TaskGroup

from services.ds_services.load_ds_translated_forecast import (
    need_to_translate_forecast_data,
    truncate_buffer_table,
    load_forecast_data_to_buffer,
    load_from_buffer_to_ds,
)

dag_params = {
    'dag_id': 'load_ds_forecast_translate_data_dag',
    'description': 'Даг перевода и загрузки переведенных данных в DS слое',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ds', 'translate', 'forecast'],
}

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    need_to_translate_forecast_data = BranchPythonOperator(
        task_id='need_to_translate_forecast_data',
        python_callable=need_to_translate_forecast_data,
    )

    load_needed = EmptyOperator(task_id='load_needed')

    with TaskGroup(group_id='load_translate_to_buffer', prefix_group_id=False) as load_buffer_group:

        truncate_buffer_table = PythonOperator(
            task_id='truncate_buffer_table',
            task_group=load_buffer_group,
            python_callable=truncate_buffer_table,
        )

        load_forecast_data_to_buffer = PythonOperator(
            task_id='load_forecast_data_to_buffer',
            task_group=load_buffer_group,
            python_callable=load_forecast_data_to_buffer,
        )

        truncate_buffer_table >> load_forecast_data_to_buffer

    load_from_buffer_to_ds = PythonOperator(
        task_id='load_from_buffer_to_ds',
        python_callable=load_from_buffer_to_ds,
    )

    finish = EmptyOperator(task_id='finish', trigger_rule='none_failed_min_one_success')

    start >> \
        need_to_translate_forecast_data >> \
        finish

    need_to_translate_forecast_data >> \
        load_needed >> \
        load_buffer_group >> \
        load_from_buffer_to_ds >> \
        finish
