-- Version 1.0
-- Selects the level and total experience of a user

SELECT level, xp, total_xp
FROM user_rank
WHERE guild_id = $1
AND user_id = $2
