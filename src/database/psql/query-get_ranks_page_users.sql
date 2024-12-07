-- Version 1.0
-- Get users with experience on the specified guild

SELECT user_id, level, xp, total_xp
FROM user_rank
WHERE guild_id = $1
ORDER BY total_xp DESC
LIMIT $2 OFFSET $3;