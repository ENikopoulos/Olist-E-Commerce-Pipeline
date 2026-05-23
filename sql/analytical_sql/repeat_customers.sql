CREATE OR REPLACE VIEW vw_repeat_customer_segments AS
WITH customer_total_orders AS 
(
    SELECT 
        customer_unique_id AS customer,
        COUNT(*) AS total_orders,
    CASE
        WHEN COUNT(*) = 1 THEN '1 order'
        WHEN COUNT(*) = 2 THEN '2 orders'
        WHEN COUNT(*)  = 3 THEN '3 orders'
    ELSE
        '4+ orders'
    END AS customer_segment
    FROM 
        fact_orders
    GROUP BY
        customer_unique_id
)

SELECT 
    customer_segment,
    COUNT(*) AS number_of_customers,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 3) AS percentage_of_customers
FROM 
    customer_total_orders
GROUP BY 
    customer_segment
ORDER BY
    number_of_customers DESC;