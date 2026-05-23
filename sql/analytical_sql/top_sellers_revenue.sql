-- Top sellers by revenue

CREATE OR REPLACE VIEW vw_top_sellers AS
WITH sellers_revenue AS (
    SELECT 
        a.seller_id,
        a.seller_state AS state,
        SUM(b.price + b.freight_value) AS total_revenue,
        COUNT(*) AS items_sold,
        ROUND(AVG(b.price + b.freight_value)::numeric, 2) AS average_item_value
    FROM
        dim_sellers a
    INNER JOIN
        fact_order_items b
        ON a.seller_id = b.seller_id
    GROUP BY
        a.seller_id
)

SELECT
    *,
    RANK() OVER(ORDER BY total_revenue DESC) AS seller_revenue_rank
FROM
    sellers_revenue;