-- Version 1.0
-- Stores settings for each channel allowing users to gain experience by chatting

CREATE TABLE "channel_experience" (
    "guild_id" BIGINT,
    "channel_id" BIGINT,
    "default_multiplier" REAL,
    PRIMARY KEY ("channel_id")
)
