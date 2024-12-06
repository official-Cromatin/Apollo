-- Version 1.0
-- Sets the level of a user to the specified value and resets the experience

UPDATE user_rank
SET level = $1, 
    xp = 0
WHERE guild_id = $2
AND user_id = $2
