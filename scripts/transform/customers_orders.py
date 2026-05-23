# Imports 
import pandas as pd
import numpy as np 
from pathlib import Path

BASE_DIR = Path("/opt/airflow")
RAW_DIR = BASE_DIR / "data" / "raw"
TRANSFORMED_DIR = BASE_DIR / "data" / "transformed"

# Customers & Orders tables data transformation

dim_customers = pd.read_csv(RAW_DIR / 'olist_customers_dataset.csv')
fact_orders = pd.read_csv(RAW_DIR / 'olist_orders_dataset.csv')

# Customers needs no transformations. Add customers_unique_id to fact_orders table

cust_id = dim_customers[['customer_id','customer_unique_id']]
fact_orders = fact_orders.merge(cust_id, 
    on  = 'customer_id',
    how = 'left',
    validate = 'many_to_one')

# From str to datetime

fact_orders['purchase_datetime'] = pd.to_datetime(fact_orders['order_purchase_timestamp'], errors = 'coerce')
fact_orders['approved_datetime'] = pd.to_datetime(fact_orders['order_approved_at'], errors = 'coerce')
fact_orders['delivered_carrier_datetime'] = pd.to_datetime(fact_orders['order_delivered_carrier_date'], errors = 'coerce')
fact_orders['delivered_customer_datetime'] = pd.to_datetime(fact_orders['order_delivered_customer_date'], errors = 'coerce')
fact_orders['estimated_delivery_datetime'] = pd.to_datetime(fact_orders['order_estimated_delivery_date'], errors = 'coerce')

# Handling missing data

fact_orders['approval_imputed'] = fact_orders['order_approved_at'].isna()     # Flag imputed
fact_orders['approval_delay'] = fact_orders['approved_datetime'] - fact_orders['purchase_datetime'] # Calculate approval delay

# Fill missing approval dates

fact_orders['order_approved_at_filled'] = fact_orders['approved_datetime'].fillna(
    fact_orders['purchase_datetime'] + fact_orders['approval_delay'].mean().round('min')
)

# Fill delivered fact_orders with NULL order_delivered_customer_date

mask = (fact_orders['order_delivered_customer_date'].isnull()) & (fact_orders['order_status'] == 'delivered')
fact_orders.loc[mask, 'delivered_customer_datetime'] = fact_orders.loc[mask, 'estimated_delivery_datetime']   # Filling missing values with estimated delivery values
fact_orders['delivery_imputed'] = mask   # Track changes

# Mark general inconsistencies

fact_orders['missing_delivery_info'] = fact_orders['order_delivered_customer_date'].isna()    # Missing delivery info

fact_orders['canceled_with_delivery'] =(
    (fact_orders['order_status'] == 'canceled') &                # Canceled but with delivery date not null
    (fact_orders['order_delivered_customer_date'].notna())
)

# New column order

fact_orders = fact_orders[['order_id', 'customer_id', 'customer_unique_id', 'order_status', 'purchase_datetime', 
       'approved_datetime', 'order_approved_at_filled', 'delivered_carrier_datetime', 
       'delivered_customer_datetime', 'estimated_delivery_datetime', 'canceled_with_delivery', 
       'approval_imputed', 'delivery_imputed']]

# Export to CSV

fact_orders.to_csv(TRANSFORMED_DIR / 'fact_orders.csv', index=False, encoding = 'utf-8')
dim_customers.to_csv(TRANSFORMED_DIR / 'dim_customers.csv', index=False, encoding = 'utf-8')