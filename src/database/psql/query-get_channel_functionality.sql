-- Version 1.0
-- Selects the enabled functionality for a specific channel

SELECT experience, pick_money
FROM event_message
WHERE channel_id = $1