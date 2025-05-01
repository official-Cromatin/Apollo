-- Version 1.0
-- Updates the last_loaded field of the view state

UPDATE view_state
SET last_loaded = $4
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;
