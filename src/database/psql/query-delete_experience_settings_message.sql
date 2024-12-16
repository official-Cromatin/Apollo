-- Version 1.0
-- Deletes the data for the matching configuration message

DELETE FROM channel_experience_settings
WHERE message_id = $1
