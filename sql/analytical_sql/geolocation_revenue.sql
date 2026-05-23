-- Revenue by state

CREATE OR REPLACE VIEW vw_geolocatio_seller_revenue AS
SELECT
    a.seller_id,
    a.seller_zip_code_prefix AS zip_code,
    b.geolocation_lat AS latitude,
    b.geolocation_lng AS longitude,
    a.seller_city AS city,
    a.seller_state AS state,
    ROUND(SUM(c.price + c.freight_value)::numeric, 2) AS revenue
FROM
    dim_sellers a
INNER JOIN
    dim_geolocation b
    ON a.seller_zip_code_prefix = b.geolocation_zip_code_prefix
INNER JOIN
    fact_order_items c
    ON c.seller_id = a.seller_id
GROUP BY
    a.seller_id, zip_code, latitude, longitude, city, state
ORDER BY
    revenue DESC;