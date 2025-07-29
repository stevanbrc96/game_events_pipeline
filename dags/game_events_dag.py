# ==============================================================================
# FAJL: game_events_dag.py
# LOKACIJA: /opt/airflow/dags/
# IZMENA: Povećano vreme rada producer-a da bi se generisalo dovoljno podataka.
# ==============================================================================
from __future__ import annotations
import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

from producer import run_producer_for_duration
from consumer import run_consumer_for_batch
from aggregations import run_aggregation
from train_model import train_churn_model

with DAG(
    dag_id="game_events_pipeline",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule="*/15 * * * *",
    tags=["nordeus_project"],
) as dag:
    
    producer_task = PythonOperator(
        task_id="run_producer_task",
        python_callable=run_producer_for_duration,
        # Povećavamo vreme rada da bismo sigurno generisali dovoljno "starih" i "novih" podataka
        op_kwargs={'duration_seconds': 90},
    )

    consumer_task = PythonOperator(
        task_id="run_consumer_task",
        python_callable=run_consumer_for_batch,
    )

    aggregation_task = PythonOperator(
        task_id="run_aggregation_task",
        python_callable=run_aggregation,
    )

    training_task = PythonOperator(
        task_id="run_training_task",
        python_callable=train_churn_model,
    )

    producer_task >> consumer_task >> aggregation_task >> training_task