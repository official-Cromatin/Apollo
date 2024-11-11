-- Version 1.0
-- Get nine users on the current page
SELECT user_id, balance
FROM money
WHERE guild_id = $1
ORDER BY balance DESC
LIMIT $2 OFFSET $3;
