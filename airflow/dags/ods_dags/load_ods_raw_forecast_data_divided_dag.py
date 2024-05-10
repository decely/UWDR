from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

from services.ods_services.load_ods_raw_forecast_divided import (
    need_to_divide_forecast_data,
    load_raw_divided_forecast_data,
    prepare_load_raw_divided_data,
)


dag_params = {
    'dag_id': 'load_ods_raw_forecast_data_divided_dag',
    'description': 'Даг разделения сырых данных прогноза погоды',
    'schedule_interval': None,
    'start_date': datetime(2024, 1, 1),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['ods', 'raw', 'forecast'],
}

with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    need_to_divide_forecast_data = BranchPythonOperator(
        task_id='need_to_divide_forecast_data',
        python_callable=need_to_divide_forecast_data,
    )

    load_needed = EmptyOperator(task_id='load_needed')

    prepare_load_raw_divided_data = PythonOperator(
        task_id='prepare_load_raw_divided_data'
        python_callable=prepare_load_raw_divided_data,
        do_xcom_push=True,
    )

    load_raw_divided_forecast_data = PythonOperator(
        task_id='load_raw_divided_forecast_data',
        python_callable=load_raw_divided_forecast_data,
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        need_to_divide_forecast_data >> \
        finish

    start >> \
        need_to_divide_forecast_data >> \
        load_needed >> \
        load_raw_divided_forecast_data >> \
        finish
