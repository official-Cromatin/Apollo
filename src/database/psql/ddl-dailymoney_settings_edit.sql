-- Version 1.0
-- Stores informations about the "add role" and "edit role" view

CREATE TABLE "dailymoney_settings_edit" (
    "message_id" BIGINT,
    "main_message_id" BIGINT,
    "role_id" BIGINT,
    "priority" SMALLINT,
    "daily_salary" SMALLINT,
    "edit_mode" SMALLINT,
    "expiration" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("message_id")
)