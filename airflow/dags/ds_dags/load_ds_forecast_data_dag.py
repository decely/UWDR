from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

from services.ds_services.load_ds_forecast import load_forecast_data_from_ods_to_ds, need_to_load_forecast_data

dag_params = {
    'dag_id': 'load_ds_forecast_data_dag',
    'description': 'Даг загрузки данных прогноза из ODS в DS слой',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ds', 'forecast'],
}

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    need_to_load_forecast_data = BranchPythonOperator(
        task_id='need_to_load_forecast_data',
        python_callable=need_to_load_forecast_data,
    )

    load_needed = EmptyOperator(task_id='load_needed')

    load_forecast_data_from_ods_to_ds = PythonOperator(
        task_id='load_forecast_data_from_ods_to_ds',
        python_callable=load_forecast_data_from_ods_to_ds,
    )

    finish = EmptyOperator(task_id='finish', trigger_rule='none_failed_min_one_success')

    start >> \
        need_to_load_forecast_data >> \
        finish

    need_to_load_forecast_data >> \
        load_needed >> \
        load_forecast_data_from_ods_to_ds >> \
        finish
