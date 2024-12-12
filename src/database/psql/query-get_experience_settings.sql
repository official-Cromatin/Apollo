-- Version 1.0
-- Selects the applied settings for the specified channel

SELECT default_multiplier, minimum_threshold, maximum_experience
FROM channel_experience
WHERE channel_id = $1