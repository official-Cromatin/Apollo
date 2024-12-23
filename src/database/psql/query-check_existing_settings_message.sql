-- Version 1.0
-- Select a settings message in the given channel, to check for its existence

SELECT message_id
FROM channel_experience_settings
WHERE channel_id = $1
