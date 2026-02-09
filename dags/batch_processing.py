from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta



default_args = {
    'owner': 'you',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 1),
}

with DAG(
    'batch_processing_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='A DAG to run the batch data pipeline',
) as dag:

    run_batch_pipeline = BashOperator(
        task_id='run_batch_pipeline',
        bash_command='python /opt/airflow/main.py --mode batch',
    )

    run_batch_pipeline