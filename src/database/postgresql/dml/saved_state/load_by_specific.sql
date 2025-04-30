-- Version 1.0
-- Selects the specified view data by guild, channel and message id

SELECT state, view_name, creation_date
FROM view_state
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;
