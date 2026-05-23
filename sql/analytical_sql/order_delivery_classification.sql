-- Late vs Early deliveries

CREATE OR REPLACE VIEW vw_delivery_classification AS
WITH classified_orders AS (
    SELECT
        order_id,
    CASE
        WHEN delivered_customer_date::date > estimated_delivery_date::date THEN 'Late'
        WHEN delivered_customer_date::date < estimated_delivery_date::date THEN 'Early'
        ELSE
            'On-time'
    END AS order_classification
FROM
    fact_orders
WHERE delivered_customer_date IS NOT NULL
)

SELECT
    order_classification,
    COUNT(*) AS number_of_orders,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER(), 2) * 100 AS percentage_of_orders
FROM
    classified_orders
GROUP BY
    order_classification;