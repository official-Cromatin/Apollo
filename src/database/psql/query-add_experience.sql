-- Version 1.0
-- Add to the user's experience on a specific guild

INSERT INTO "user_rank" ("guild_id", "user_id", "xp", "total_xp")
VALUES ($1, $2, $3, $3)
ON CONFLICT ("guild_id", "user_id")
DO UPDATE SET xp = user_rank.xp + $3
              total_xp = user_rank.total_xp + $3
WHERE user_rank.guild_id = $1
AND user_rank.user_id = $2
