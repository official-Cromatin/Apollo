-- Version 1.0
-- Stores what features are enabled for each individual channel

CREATE TABLE "event_message" (
    "guild_id" BIGINT,
    "channel_id" BIGINT,
    "experience" BOOLEAN DEFAULT FALSE,
    PRIMARY KEY ("channel_id")
)