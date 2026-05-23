-- Create tables for the E-Commerce Database

-- Geolocation Table
CREATE TABLE IF NOT EXISTS dim_geolocation (
    geolocation_zip_code_prefix INT PRIMARY KEY NOT NULL,
    geolocation_lat DOUBLE PRECISION,
    geolocation_lng DOUBLE PRECISION,
    geolocation_city TEXT,
    geolocation_state TEXT
);

-- Customers Table
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY NOT NULL,
    customer_unique_id TEXT,
    customer_zip_code_prefix INT,
    customer_city TEXT,
    customer_state TEXT,
    FOREIGN KEY (customer_zip_code_prefix) 
        REFERENCES dim_geolocation(geolocation_zip_code_prefix) 
        ON DELETE SET NULL
);

-- Sellers Table
CREATE TABLE IF NOT EXISTS dim_sellers (
    seller_id TEXT PRIMARY KEY NOT NULL,
    seller_zip_code_prefix INT,
    seller_city TEXT,
    seller_state TEXT,
    FOREIGN KEY (seller_zip_code_prefix)
        REFERENCES dim_geolocation(geolocation_zip_code_prefix) 
        ON DELETE SET NULL
);

-- Products Table
CREATE TABLE IF NOT EXISTS dim_products (
    product_id TEXT PRIMARY KEY NOT NULL,
    product_category_name TEXT,
    product_category_name_english TEXT,
    product_name_length FLOAT,
    product_description_length FLOAT,
    product_photos_qty FLOAT,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    product_category_name_filled TEXT,
    category_filled BOOLEAN
);

-- Orders Table
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id TEXT PRIMARY KEY NOT NULL,
    customer_id TEXT,
    customer_unique_id TEXT,
    order_status TEXT,
    purchase_datetime TIMESTAMP,
    approved_datetime TIMESTAMP,
    order_approved_at_filled TIMESTAMP,
    delivered_carrier_date TIMESTAMP,
    delivered_customer_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    canceled_with_delivery BOOLEAN,
    approval_imputed BOOLEAN,
    delivery_imputed BOOLEAN,
    FOREIGN KEY (customer_id) 
        REFERENCES dim_customers(customer_id)
        ON DELETE SET NULL
);

-- Order Items Table
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_id TEXT,
    order_item_id INT NOT NULL,
    product_id TEXT,
    seller_id TEXT,
    price FLOAT,
    freight_value FLOAT,
    shipping_limit_date TIMESTAMP,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) 
        REFERENCES dim_products(product_id),
    FOREIGN KEY (seller_id) 
        REFERENCES dim_sellers(seller_id) 
        ON DELETE SET NULL
);

-- Payments Table
CREATE TABLE IF NOT EXISTS fact_payments (
    order_id TEXT,
    payment_sequential INT NOT NULL,
    payment_type TEXT,
    payment_installments INT,
    payment_value FLOAT,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) 
        ON DELETE CASCADE
);


-- Reviews Table
CREATE TABLE IF NOT EXISTS fact_reviews (
    review_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date DATE,
    review_answer_timestamp TIMESTAMP,
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id)
        ON DELETE CASCADE
);

-- Index creation
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON fact_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_items_order_id ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_product_id ON fact_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_items_seller_id ON fact_order_items(seller_id);