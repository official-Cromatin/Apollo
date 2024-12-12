-- Version 1.0
-- Stores settings for each channel allowing the apperance of pick money 

CREATE TABLE "channel_pick_money" (
    "guild_id" BIGINT,
    "channel_id" BIGINT,
    "min_amount" SMALLINT,
    "max_amount" SMALLINT,
    "probability" SMALLINT,
    PRIMARY KEY ("channel_id")
)
