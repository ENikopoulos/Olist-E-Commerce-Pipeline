-- Review score distribution

CREATE OR REPLACE VIEW vw_review_score_distribution AS
SELECT 
    review_score,
    COUNT(*) AS number_of_reviews,
   ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER(), 2) * 100 AS percentage_of_reviews,
CASE
    WHEN review_score = 1 THEN '1 star'
    WHEN review_score = 2 THEN '2 stars'
    WHEN review_score = 3 THEN '3 stars'
    WHEN review_score = 4 THEN '4 stars'
    ELSE '5 stars'
END AS score_label
FROM
    fact_reviews
GROUP BY
    review_score
ORDER BY review_score ASC;