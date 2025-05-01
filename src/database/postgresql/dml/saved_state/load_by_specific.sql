-- Version 2.0
-- Selects the specified view data by guild, channel and message id

SELECT id, state, view_name, timeout, creation_date, last_loaded, last_updated
FROM view_state
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;

UPDATE view_state
SET last_loaded = $4
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;
