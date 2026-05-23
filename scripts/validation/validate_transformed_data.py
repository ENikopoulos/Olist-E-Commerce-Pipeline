from pathlib import Path
import pandas as pd


BASE_DIR = Path("/opt/airflow")
RAW_DIR = BASE_DIR / "data" / "raw"
TRANSFORMED_DIR = BASE_DIR / "data" / "transformed"


def load_transformed_tables() -> dict[str, pd.DataFrame]:
    """Load all transformed CSV files into DataFrames."""
    return {
        "dim_customers": pd.read_csv(TRANSFORMED_DIR / "dim_customers.csv"),
        "dim_sellers": pd.read_csv(TRANSFORMED_DIR / "dim_sellers.csv"),
        "dim_products": pd.read_csv(TRANSFORMED_DIR / "dim_products.csv"),
        "dim_geolocation": pd.read_csv(TRANSFORMED_DIR / "dim_geolocation.csv"),
        "fact_orders": pd.read_csv(TRANSFORMED_DIR / "fact_orders.csv"),
        "fact_order_items": pd.read_csv(TRANSFORMED_DIR / "fact_order_items.csv"),
        "fact_payments": pd.read_csv(TRANSFORMED_DIR / "fact_payments.csv"),
        "fact_reviews": pd.read_csv(TRANSFORMED_DIR / "fact_reviews.csv"),
    }


def assert_primary_keys(tables: dict[str, pd.DataFrame]) -> None:
    """Validate primary key uniqueness and non-nullness."""
    checks = {
        "dim_customers": ["customer_id"],
        "dim_sellers": ["seller_id"],
        "dim_products": ["product_id"],
        "dim_geolocation": ["geolocation_zip_code_prefix"],
        "fact_orders": ["order_id"],
        "fact_order_items": ["order_id", "order_item_id"],
        "fact_payments": ["order_id", "payment_sequential"],
        "fact_reviews": ["review_id", "order_id"],
    }

    for table_name, pk_cols in checks.items():
        df = tables[table_name]

        if df[pk_cols].isna().any().any():
            raise ValueError(f"{table_name}: NULL values found in primary key columns {pk_cols}")

        if df.duplicated(pk_cols).any():
            duplicate_count = df.duplicated(pk_cols).sum()
            raise ValueError(
                f"{table_name}: {duplicate_count} duplicate primary key values found for {pk_cols}"
            )


def assert_foreign_keys(tables: dict[str, pd.DataFrame]) -> None:
    """Validate foreign key coverage between fact and dimension tables."""
    dim_customers = tables["dim_customers"]
    dim_sellers = tables["dim_sellers"]
    dim_products = tables["dim_products"]
    dim_geolocation = tables["dim_geolocation"]

    fact_orders = tables["fact_orders"]
    fact_order_items = tables["fact_order_items"]
    fact_payments = tables["fact_payments"]
    fact_reviews = tables["fact_reviews"]

    fk_checks = [
        (
            "fact_orders.customer_id",
            fact_orders["customer_id"],
            "dim_customers.customer_id",
            dim_customers["customer_id"],
        ),
        (
            "dim_customers.customer_zip_code_prefix",
            dim_customers["customer_zip_code_prefix"],
            "dim_geolocation.geolocation_zip_code_prefix",
            dim_geolocation["geolocation_zip_code_prefix"],
        ),
        (
            "dim_sellers.seller_zip_code_prefix",
            dim_sellers["seller_zip_code_prefix"],
            "dim_geolocation.geolocation_zip_code_prefix",
            dim_geolocation["geolocation_zip_code_prefix"],
        ),
        (
            "fact_order_items.order_id",
            fact_order_items["order_id"],
            "fact_orders.order_id",
            fact_orders["order_id"],
        ),
        (
            "fact_order_items.product_id",
            fact_order_items["product_id"],
            "dim_products.product_id",
            dim_products["product_id"],
        ),
        (
            "fact_order_items.seller_id",
            fact_order_items["seller_id"],
            "dim_sellers.seller_id",
            dim_sellers["seller_id"],
        ),
        (
            "fact_payments.order_id",
            fact_payments["order_id"],
            "fact_orders.order_id",
            fact_orders["order_id"],
        ),
        (
            "fact_reviews.order_id",
            fact_reviews["order_id"],
            "fact_orders.order_id",
            fact_orders["order_id"],
        ),
    ]

    for child_name, child_values, parent_name, parent_values in fk_checks:
        missing = set(child_values.dropna()) - set(parent_values.dropna())

        if missing:
            sample = list(missing)[:10]
            raise ValueError(
                f"Foreign key violation: {child_name} contains values not found in {parent_name}. "
                f"Missing count: {len(missing)}. Sample: {sample}"
            )


def assert_business_rules(tables: dict[str, pd.DataFrame]) -> None:
    """Validate important business and data quality rules."""
    fact_orders = tables["fact_orders"]
    fact_order_items = tables["fact_order_items"]
    fact_payments = tables["fact_payments"]
    fact_reviews = tables["fact_reviews"]

    # Numeric fields should not be negative
    numeric_non_negative_checks = [
        ("fact_order_items.price", fact_order_items["price"]),
        ("fact_order_items.freight_value", fact_order_items["freight_value"]),
        ("fact_payments.payment_value", fact_payments["payment_value"]),
        ("fact_payments.payment_installments", fact_payments["payment_installments"]),
    ]

    for field_name, series in numeric_non_negative_checks:
        invalid_count = (series.dropna() < 0).sum()
        if invalid_count > 0:
            raise ValueError(f"{field_name}: found {invalid_count} negative values")

    # Review scores should be between 1 and 5
    invalid_reviews = ~fact_reviews["review_score"].between(1, 5)
    if invalid_reviews.any():
        raise ValueError(f"fact_reviews.review_score: found {invalid_reviews.sum()} invalid scores")

    # Required order fields
    required_order_cols = ["order_id", "customer_id", "order_status", "purchase_datetime"]
    missing_required = fact_orders[required_order_cols].isna().sum()
    missing_required = missing_required[missing_required > 0]

    if not missing_required.empty:
        raise ValueError(f"fact_orders: missing required values:\n{missing_required}")


def validate_all() -> None:
    """Run all validation checks."""
    tables = load_transformed_tables()

    assert_primary_keys(tables)
    assert_foreign_keys(tables)
    assert_business_rules(tables)

    print("All transformed data validation checks passed successfully.")


if __name__ == "__main__":
    validate_all()