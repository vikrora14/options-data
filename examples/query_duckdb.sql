-- Example: Query options data directly with DuckDB
-- No download required - DuckDB can read Parquet from HTTP

-- Average implied volatility by expiration
SELECT 
    expiration,
    type,
    COUNT(*) as contracts,
    AVG(implied_volatility) as avg_iv,
    AVG(delta) as avg_delta
FROM 'https://static.philippdubach.com/data/options/spy/options.parquet'
WHERE date = '2025-12-16'
GROUP BY expiration, type
ORDER BY expiration, type;

-- Most liquid contracts by open interest
SELECT 
    symbol,
    expiration,
    strike,
    type,
    open_interest,
    volume,
    implied_volatility,
    delta
FROM 'https://static.philippdubach.com/data/options/spy/options.parquet'
WHERE date = '2025-12-16'
ORDER BY open_interest DESC
LIMIT 20;

-- IV surface for a specific date
SELECT 
    strike,
    expiration,
    implied_volatility
FROM 'https://static.philippdubach.com/data/options/spy/options.parquet'
WHERE date = '2025-12-16'
  AND type = 'call'
  AND implied_volatility IS NOT NULL
ORDER BY expiration, strike;
