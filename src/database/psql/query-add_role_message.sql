-- Version 1.0
-- Inserts a row into the table to store data about the created add role view

INSERT INTO dailymoney_settings ("main_message_id", "message_id", "edit_mode")
VALUES ($1, $2, $3)