# Imports 

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("/opt/airflow")
RAW_DIR = BASE_DIR / "data" / "raw"
TRANSFORMED_DIR = BASE_DIR / "data" / "transformed"

# Sellers, Geolocation and Order Reviews tables

fact_reviews = pd.read_csv(RAW_DIR / 'olist_order_reviews_dataset.csv')
dim_geolocation = pd.read_csv(RAW_DIR / 'olist_geolocation_dataset.csv')
dim_sellers = pd.read_csv(RAW_DIR / 'olist_sellers_dataset.csv')
temp_customers = pd.read_csv(RAW_DIR / 'olist_customers_dataset.csv')

# Geolocation transformations

dim_geolocation = dim_geolocation.drop_duplicates()     # Drop exact duplicates

# Many zip codes with slightly different lat and lng - Aggregate to one row per zip

dim_geolocation = (
    dim_geolocation
    .groupby('geolocation_zip_code_prefix', as_index=False)
    .agg({
        'geolocation_lat': 'mean',
        'geolocation_lng': 'mean',
        'geolocation_city': 'first',
        'geolocation_state': 'first'
    })
)

# Fill missing zip codes from sellers and customers tables

missing_zips_customer = set(temp_customers['customer_zip_code_prefix']) - set(dim_geolocation['geolocation_zip_code_prefix'])

missing_zips_seller = set(dim_sellers['seller_zip_code_prefix']) - set(dim_geolocation['geolocation_zip_code_prefix'])

# Create placeholder rows for missing zips

missing_zips = list(missing_zips_customer) + list(missing_zips_seller)

missing_rows = pd.DataFrame({
    'geolocation_zip_code_prefix': list(missing_zips),
    'geolocation_lat': None,
    'geolocation_lng': None,
    'geolocation_city': None,
    'geolocation_state': None
})

# Fill city and state data from customers table

missing_rows = missing_rows.merge(temp_customers, left_on = 'geolocation_zip_code_prefix', right_on = 'customer_zip_code_prefix', how = 'left')
missing_rows['geolocation_city'] = missing_rows['customer_city']
missing_rows['geolocation_state'] = missing_rows['customer_state']
missing_rows = missing_rows[['geolocation_zip_code_prefix', 'geolocation_lat', 
                             'geolocation_lng', 'geolocation_city', 'geolocation_state']].drop_duplicates()

# Fill city and state date from sellers table

missing_rows = missing_rows.merge(dim_sellers, left_on = 'geolocation_zip_code_prefix', right_on = 'seller_zip_code_prefix', how = 'left')
missing_rows['geolocation_city'] = missing_rows['geolocation_city'].fillna(missing_rows['seller_city'])
missing_rows['geolocation_state'] = missing_rows['geolocation_state'].fillna(missing_rows['seller_state'])
missing_rows = missing_rows[['geolocation_zip_code_prefix', 'geolocation_lat', 
                             'geolocation_lng', 'geolocation_city', 'geolocation_state']].drop_duplicates()

# Add rows to geolocation table

dim_geolocation = pd.concat([dim_geolocation, missing_rows], ignore_index=True)

# Reviews transformations

fact_reviews['review_creation_date'] = pd.to_datetime(fact_reviews['review_creation_date'], errors = 'coerce')     # From str to datetime
fact_reviews['review_answer_timestamp'] = pd.to_datetime(fact_reviews['review_answer_timestamp'], errors = 'coerce')      # From str to datetime

# Sellers table needs no transformation!

# Export to CSV

dim_sellers.to_csv(TRANSFORMED_DIR / 'dim_sellers.csv',index=False, encoding = 'utf-8')
dim_geolocation.to_csv(TRANSFORMED_DIR / 'dim_geolocation.csv', index = False, encoding = 'utf-8')
fact_reviews.to_csv(TRANSFORMED_DIR / 'fact_reviews.csv', index = False, encoding = 'utf-8')