from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow"


with DAG(
    dag_id="olist_ecommerce_etl_pipeline",
    description="Transform, validate, and load Olist e-commerce data into PostgreSQL",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["ecommerce", "postgres", "etl"],
) as dag:

    transform_customers_orders = BashOperator(
        task_id="transform_customers_orders",
        bash_command=f"python {PROJECT_ROOT}/scripts/transform/customers_orders.py",
    )

    transform_products_items_payments = BashOperator(
        task_id="transform_products_items_payments",
        bash_command=f"python {PROJECT_ROOT}/scripts/transform/products_order_items_payments.py",
    )

    transform_reviews_sellers_geolocation = BashOperator(
        task_id="transform_reviews_sellers_geolocation",
        bash_command=f"python {PROJECT_ROOT}/scripts/transform/reviews_sellers_geolocation.py",
    )

    validate_transformed_data = BashOperator(
        task_id="validate_transformed_data",
        bash_command=f"python {PROJECT_ROOT}/scripts/validation/validate_transformed_data.py",
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command=f"python {PROJECT_ROOT}/scripts/load/load_postgres.py",
    )

    [
        transform_customers_orders,
        transform_products_items_payments,
        transform_reviews_sellers_geolocation,
    ] >> validate_transformed_data >> load_postgres