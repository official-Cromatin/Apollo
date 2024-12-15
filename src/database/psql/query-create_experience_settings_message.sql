-- Version 1.0
-- Insers a row into the "experience_settings_message" table to store data about the configuration message

INSERT INTO channel_experience_settings ("channel_id", "message_id", "original_message_id", "default_multiplier", "minimum_threshold", "maximum_experience")
VALUES ($1, $2, $3, $4, $5, $6)
