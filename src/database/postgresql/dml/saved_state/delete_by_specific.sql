-- Version 1.0
-- Deletes the view identified by guild, channel and message

DELETE FROM view_states
WHERE guild_id = $1
AND channel_id = $2
AND message_id = $3;
