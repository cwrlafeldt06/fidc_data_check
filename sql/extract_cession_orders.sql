-- Extract cession orders data from BigQuery for comparison with fund reports
-- Tables: maindb.cessions, maindb.cession_orders, maindb.buyers
-- Comparison focus: ValorAquisicao vs payable, ValorFace vs receivable
-- Filter: buyer alias ('ai', 'pi') with proper date conditions

SELECT 
    -- Core identification for matching
    co.id as NumeroContrato,  -- Map internal 'id' to 'NumeroContrato' for comparison
    
    -- Aggregated fields for comparison (mapped to fund report column names)
    SUM(ce.receivable) as ValorFace,        -- Compare with ValorFace from fund reports
    SUM(ce.payable) as ValorAquisicao,      -- Compare with ValorAquisicao from fund reports
    
    -- Additional context fields
    COUNT(ce.id) as NumCessions,            -- Number of individual cessions
    b.alias as FundAlias                    -- Fund identifier ('ai' or 'pi')

FROM `infinitepay-production.maindb.cessions` ce 
INNER JOIN `infinitepay-production.maindb.cession_orders` co ON co.id = ce.cession_order_id 
INNER JOIN `infinitepay-production.maindb.buyers` b ON b.user_id = ce.buyer_id
WHERE TRUE
    -- Filter by specific fund alias (parameterized)
    AND b.alias = '{fund_alias}'
    
    -- Date filtering conditions (proper business logic)
    AND co.created_at <= '2025-05-30'
    AND ce.buyer_payment_date > '2025-05-30'
    
GROUP BY co.id, b.alias
ORDER BY co.id 