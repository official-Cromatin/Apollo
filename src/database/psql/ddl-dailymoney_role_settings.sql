-- Version 1.0
-- Stores informations about the "add role" view

CREATE TABLE "dailymoney_add_settings" (
    "message_id" BIGINT,
    "main_message_id" BIGINT,
    "role_id" BIGINT,
    "priority" SMALLINT,
    "daily_salary" SMALLINT,
    PRIMARY KEY ("message_id")
)