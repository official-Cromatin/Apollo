-- Version 1.0
-- Select when the specified user has gained its last xp points by chatting

SELECT last_xp_pickup
FROM user_rank
WHERE user_id = $1
AND guild_id = $2