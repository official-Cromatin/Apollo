-- Version 1.0
-- Selects the matching row in the channel_experience_settings table to display them in the message

SELECT default_multiplier, minimum_threshold, maximum_experience
FROM channel_experience_settings
WHERE message_id = $1
