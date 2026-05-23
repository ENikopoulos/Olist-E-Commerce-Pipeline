-- Top 10 product categories by revenue
CREATE OR REPLACE VIEW vw_top_product_categories AS
SELECT
    b.product_category_name_english AS category_name,
    ROUND(SUM(a.price + a.freight_value) :: numeric, 2) AS revenue,
    COUNT(*) AS number_of_items_sold,
    ROUND(AVG(a.price)::numeric, 2) AS average_item_price,
    ROUND(AVG(a.price + a.freight_value)::numeric, 2) AS average_item_total_value
FROM
    fact_order_items a
JOIN
    dim_products b
        ON a.product_id = b.product_id
GROUP BY 
    category_name
ORDER BY revenue DESC
LIMIT 10;