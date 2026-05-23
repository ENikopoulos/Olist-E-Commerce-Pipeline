-- Monthly total payment value, num of orders and average order value 
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    TO_CHAR(DATE_TRUNC('month',a.purchase_datetime), 'YYYY-MM') AS month,
    ROUND(SUM(b.payment_value)::NUMERIC, 2) AS total_value,
    COUNT(DISTINCT a.order_id) AS number_of_orders,
    ROUND((SUM(b.payment_value) / COUNT( DISTINCT a.order_id))::NUMERIC, 2) AS average_value
FROM
    fact_orders a
JOIN
    fact_payments b
    ON
        a.order_id = b.order_id
GROUP BY
    month
ORDER BY month ASC;