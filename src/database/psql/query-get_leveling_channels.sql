-- Version 1.0
-- Selects all channels having leveling enabled on the specified guild

SELECT channel_id
FROM channel_experience
WHERE guild_id = $1
