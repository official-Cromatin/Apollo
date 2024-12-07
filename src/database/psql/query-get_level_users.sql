-- Version 1.0
-- Counts how many users have xp on a certain guild 

SELECT COUNT(*)
FROM user_rank
WHERE guild_id = $1
