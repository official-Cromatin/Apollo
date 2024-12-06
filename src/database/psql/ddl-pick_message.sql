-- Version 1.0
-- Stores information about the "pick money" message

CREATE TABLE "pick_money" (
    "message_id" BIGINT,
    "guild_id" BIGINT,
    "channel_id" BIGINT,
    "amount" SMALLINT,
    "creation" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("message_id")
)
