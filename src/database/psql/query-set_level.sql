-- Version 1.0
-- Sets the level of a user to the specified value and resets the experience

UPDATE user_rank
SET level = $1, 
    xp = $2
WHERE guild_id = $3
AND user_id = $4
