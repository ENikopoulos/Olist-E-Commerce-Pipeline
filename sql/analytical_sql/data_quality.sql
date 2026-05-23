-- Data quality summary

CREATE OR REPLACE VIEW vw_data_quality_summary AS
WITH data_quality AS (
    SELECT
        COUNT(*) AS total_order_count,
        COUNT(*)
            FILTER (WHERE approval_imputed) AS count_of_approvals_imputed,
        COUNT(*)
            FILTER (WHERE delivery_imputed) AS count_of_deliveries_imputed,
        COUNT(*)
            FILTER (WHERE canceled_with_delivery) AS count_of_canceled_with_delivery
    FROM
        fact_orders
)

SELECT 
    total_order_count,
    count_of_approvals_imputed,
    count_of_approvals_imputed::numeric / total_order_count::numeric AS pct_of_approvals_imputed,
    count_of_deliveries_imputed,
    count_of_deliveries_imputed::numeric / total_order_count::numeric AS pct_of_deliveries_imputed,
    count_of_canceled_with_delivery,
    count_of_canceled_with_delivery::numeric / total_order_count::numeric AS pct_of_canceled_with_delivery
FROM
    data_quality;