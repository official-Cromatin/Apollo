-- Version 2.5
-- Selects the specified view data by guild, channel and message id

SELECT id, data, view_name, timeout, active, creation_date, last_loaded, last_updated
FROM view_state
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;
