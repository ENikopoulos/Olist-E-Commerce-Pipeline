# Imports 

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("/opt/airflow")
RAW_DIR = BASE_DIR / "data" / "raw"
TRANSFORMED_DIR = BASE_DIR / "data" / "transformed"

# Products, Order Items and Order Payments 

dim_products = pd.read_csv(RAW_DIR /'olist_products_dataset.csv')
fact_order_items = pd.read_csv(RAW_DIR /'olist_order_items_dataset.csv')
fact_payments = pd.read_csv(RAW_DIR /'olist_order_payments_dataset.csv')

# English translation for product names

translation = pd.read_csv(RAW_DIR /'product_category_name_translation.csv')

# Fill translation table missing values

translation.loc[71] = ['portateis_cozinha_e_preparadores_de_alimentos', 'portable_kitchen_appliances_and_food_processors']
translation.loc[72] = ['pc_gamer', 'pc_gamer']

# Merge products table with the translation table

dim_products = dim_products.merge(translation, how = 'left', on = 'product_category_name')

# Products table transformations

dim_products['product_category_name_filled'] = dim_products['product_category_name'].fillna('missing')  # New column with filled prod category name
dim_products['category_filled'] = dim_products['product_category_name'].isna()  # Flag missng category
dim_products = dim_products[['product_id', 'product_category_name', 'product_category_name_english', 'product_name_lenght',
       'product_description_lenght', 'product_photos_qty', 'product_weight_g',
       'product_length_cm', 'product_height_cm', 'product_width_cm',
       'product_category_name_filled', 'category_filled']]

# Order items transformations

fact_order_items['shipping_limit_datetime'] = pd.to_datetime(fact_order_items['shipping_limit_date'], errors = 'coerce')     # From str to datetime
fact_order_items = fact_order_items.drop('shipping_limit_date', axis = 1)

# Payments table no transformation needed!

# Export to CSV

dim_products.to_csv(TRANSFORMED_DIR /'dim_products.csv', index=False, encoding = 'utf-8')
fact_order_items.to_csv(TRANSFORMED_DIR /'fact_order_items.csv', index=False, encoding = 'utf-8')
fact_payments.to_csv(TRANSFORMED_DIR /'fact_payments.csv', index=False, encoding = 'utf-8')