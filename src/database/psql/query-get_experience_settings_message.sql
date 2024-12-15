-- Version 1.0
-- Selects the matching row in the channel_experience_settings table to display them in the message

SELECT default_multiplier, minimum_threshold, maximum_experience, message_id, original_message_id
FROM channel_experience_settings
WHERE channel_id = $1
