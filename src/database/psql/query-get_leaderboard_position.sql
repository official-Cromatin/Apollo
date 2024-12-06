-- Version 1.0
-- Calculates the position a user has in the ranking list within a guild

SELECT rank - 1 AS user_rank
FROM (
    SELECT
        "user_id",
        "guild_id",
        "total_xp",
        RANK() OVER (
            PARTITION BY "guild_id" 
            ORDER BY "total_xp" DESC
        ) AS rank
    FROM "user_rank"
) ranked
WHERE "guild_id" = $1
  AND "user_id" = $2;