-- Version 1.0
-- Add to the user's experience on a specific guild

INSERT INTO "user_rank" ("guild_id", "user_id", "xp", "level", "total_xp")
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT ("guild_id", "user_id")
DO UPDATE SET xp = $3,
              level = $4,
              total_xp = user_rank.total_xp + $5
WHERE user_rank.guild_id = $1
AND user_rank.user_id = $2