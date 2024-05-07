from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

from services.ds_services.load_ds_translation_table import (
    need_to_update_translation_table,
    update_translate_libraries_if_needed,
    prepare_load_translate_table,
    load_translation_to_weather,
)

dag_params = {
    'dag_id': 'load_ds_translation_table_data_dag',
    'description': 'Даг загрузки таблицу для перевода данных',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ds', 'translate'],
}

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    need_to_update_translation_table = BranchPythonOperator(
        task_id='need_to_update_translation_table',
        python_callable=need_to_update_translation_table,
    )

    update_needed = EmptyOperator(task_id='update_needed')

    update_translate_libraries_if_needed = PythonOperator(
        task_id='update_translate_libraries_if_needed',
        python_callable=update_translate_libraries_if_needed,
    )

    prepare_load_translate_table = PythonOperator(
        task_id='prepare_load_translate_table',
        python_callable=prepare_load_translate_table,
        do_xcom_push=True,
    )

    load_translation_to_weather = PythonOperator(
        task_id='load_translation_to_weather',
        python_callable=load_translation_to_weather,
    )

    finish = EmptyOperator(task_id='finish', trigger_rule='none_failed_min_one_success')

    start >> \
        need_to_update_translation_table >> \
        finish

    need_to_update_translation_table >> \
        update_needed >> \
        update_translate_libraries_if_needed >> \
        prepare_load_translate_table >> \
        load_translation_to_weather >> \
        finish
