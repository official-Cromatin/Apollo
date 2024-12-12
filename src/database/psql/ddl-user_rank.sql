-- Version 2.0
-- Stores information about the level and experience of each user on different guilds

CREATE TABLE "user_rank" (
    "guild_id" BIGINT NOT NULL,
    "user_id" BIGINT NOT NULL,
    "xp" INTEGER DEFAULT 0,
    "total_xp" INTEGER DEFAULT 0,
    "level" INTEGER DEFAULT 0,
    "last_xp_pickup" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("guild_id", "user_id")
)
