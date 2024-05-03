from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


dag_params = {
    'dag_id': 'master_load_weather_data_dag',
    'description': 'DAG инициализирующий загрузку погодных данных по расписанию',
    'schedule_interval': '*/20 * * * *',
    'start_date': datetime(2024, 3, 5),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['load', 'master', 'weather'],
    'default_args': {
        'retries': 2,
        'retry_delay': timedelta(seconds=60),
    },
}


with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    trigger_load_ods_raw_weather_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ods_raw_weather_data_dag',
        trigger_dag_id='load_ods_raw_weather_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ds_weather_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ds_weather_data_dag',
        trigger_dag_id='load_ds_weather_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ds_weather_translated_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ds_weather_translated_data_dag',
        trigger_dag_id='load_ds_weather_translated_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_dm_weather_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_dm_weather_data_dag',
        trigger_dag_id='load_dm_weather_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        trigger_load_ods_raw_weather_data_dag >> \
        trigger_load_ds_weather_data_dag >> \
        trigger_load_ds_weather_translated_data_dag >> \
        trigger_load_dm_weather_data_dag >> \
        finish
