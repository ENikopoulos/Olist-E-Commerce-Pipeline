from pathlib import Path
import psycopg2


BASE_DIR = Path("/opt/airflow")
TRANSFORMED_DIR = BASE_DIR / "data" / "transformed"
SQL_DIR = BASE_DIR / "sql"

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,  # Docker Postgres; use 5432 if using Windows Postgres
    "dbname": "e_commerce",
    "user": "olist_user",
    "password": "olist_password",
}


TABLE_LOAD_ORDER = [
    "dim_geolocation",
    "dim_customers",
    "dim_sellers",
    "dim_products",
    "fact_orders",
    "fact_order_items",
    "fact_payments",
    "fact_reviews",
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def run_sql_file(conn, sql_path: Path):
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()


def truncate_tables(conn):
    """
    Truncate all tables before reload.
    CASCADE handles FK dependencies.
    """
    tables = ", ".join(TABLE_LOAD_ORDER)

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;")

    conn.commit()


def copy_csv_to_table(conn, table_name: str):
    csv_path = TRANSFORMED_DIR / f"{table_name}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")

    file_encoding = "latin1" if table_name == "fact_reviews" else "utf-8"


    copy_sql = f"""
        COPY {table_name}
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE,
            DELIMITER ',',
            NULL ''
        );
    """

    with conn.cursor() as cur:
        with open(csv_path, "r", encoding="utf-8") as f:
            cur.copy_expert(copy_sql, f)

    conn.commit()


def print_row_counts(conn):
    with conn.cursor() as cur:
        for table in TABLE_LOAD_ORDER:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"{table}: {count:,} rows")


def load_all_tables():
    with get_connection() as conn:
        print("Creating tables...")
        run_sql_file(conn, SQL_DIR / "table_creation" / "create_tables.sql")

        print("Truncating existing data...")
        truncate_tables(conn)

        for table in TABLE_LOAD_ORDER:
            print(f"Loading {table}...")
            copy_csv_to_table(conn, table)

        print("Load complete. Row counts:")
        print_row_counts(conn)


if __name__ == "__main__":
    load_all_tables()