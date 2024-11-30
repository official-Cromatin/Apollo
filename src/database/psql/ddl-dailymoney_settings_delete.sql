-- Version 1.0
-- Stores information about the "delete role" view

CREATE TABLE "dailymoney_settings_delete" (
    "message_id" BIGINT,
    "main_message_id" BIGINT,
    "role_id" BIGINT,
    "expiration" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("message_id")
)
