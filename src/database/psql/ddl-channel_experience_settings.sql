-- Version 1.0
-- Stores data about the configuration message to configure the channel for earning experience

CREATE TABLE "channel_experience_settings" (
    "message_id" BIGINT,
    "original_message_id" BIGINT,
    "default_multiplier" REAL,
    "minimum_threshold" SMALLINT,
    "maximum_experience" SMALLINT,
    "expiration" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("message_id")
)
