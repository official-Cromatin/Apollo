-- Version 1.0
-- Resets the last_xp_pickup

INSERT INTO user_rank (guild_id, user_id)
VALUES ($1, $2)
ON CONFLICT (guild_id, user_id)
DO UPDATE SET last_xp_pickup = CURRENT_TIMESTAMP;