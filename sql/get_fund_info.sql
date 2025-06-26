-- Get fund information by user_id
-- This query retrieves fund details for a specific buyer/fund ID

SELECT 
    b.user_id,
    b.alias as fund_alias,
    u.name as fund_name,
    u.document as fund_document,
    COUNT(DISTINCT ce.id) as total_cessions,
    COUNT(DISTINCT co.id) as total_orders,
    MIN(co.created_at) as first_order_date,
    MAX(co.created_at) as last_order_date
FROM `infinitepay-production.maindb.buyers` b
INNER JOIN `infinitepay-production.maindb.users` u ON u.id = b.user_id
LEFT JOIN `infinitepay-production.maindb.cessions` ce ON ce.buyer_id = b.user_id
LEFT JOIN `infinitepay-production.maindb.cession_orders` co ON co.id = ce.cession_order_id
WHERE b.user_id = {fund_user_id}
GROUP BY b.user_id, b.alias, u.name, u.document
ORDER BY b.user_id 