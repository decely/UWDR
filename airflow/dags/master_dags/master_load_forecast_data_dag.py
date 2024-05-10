from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


dag_params = {
    'dag_id': 'master_load_forecast_data_dag',
    'description': 'DAG инициализирующий загрузку данных прогноза по расписанию',
    'schedule_interval': '30 12 * * *',
    'start_date': datetime(2024, 3, 5),
    'max_active_tasks': 1,
    'max_active_runs': 1,
    'catchup': False,
    'tags': ['load', 'master', 'forecast'],
    'default_args': {
        'retries': 2,
        'retry_delay': timedelta(seconds=60),
    },
}


with DAG(**dag_params) as dag:  # type: ignore
    start = EmptyOperator(task_id='start')

    trigger_load_ods_raw_forecast_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ods_raw_forecast_data_dag',
        trigger_dag_id='load_ods_raw_forecast_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ods_raw_forecast_data_divided_dag = TriggerDagRunOperator(
        task_id='trigger_load_ods_forecast_data_divided_dag',
        trigger_dag_id='load_ods_forecast_data_divided_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ds_forecast_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ds_forecast_data_dag',
        trigger_dag_id='load_ds_forecast_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ds_forecast_translated_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ds_forecast_translated_data_dag',
        trigger_dag_id='load_ds_forecast_translate_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_ds_translation_table_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_ds_translation_table_data_dag',
        trigger_dag_id='load_ds_translation_table_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_dm_forecast_actual_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_dm_forecast_actual_data_dag',
        trigger_dag_id='load_dm_forecast_actual_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    trigger_load_dm_forecast_all_data_dag = TriggerDagRunOperator(
        task_id='trigger_load_dm_forecast_all_data_dag',
        trigger_dag_id='load_dm_forecast_all_data_dag',
        wait_for_completion=True,
        poke_interval=10,
        trigger_rule='all_done',
    )

    finish = EmptyOperator(task_id='finish')

    start >> \
        trigger_load_ods_raw_forecast_data_dag >> \
        trigger_load_ods_raw_forecast_data_divided_dag >> \
        trigger_load_ds_forecast_data_dag >> \
        trigger_load_ds_translation_table_data_dag >> \
        trigger_load_ds_forecast_translated_data_dag >> \
        trigger_load_dm_forecast_actual_data_dag >> \
        trigger_load_dm_forecast_all_data_dag >> \
        finish
