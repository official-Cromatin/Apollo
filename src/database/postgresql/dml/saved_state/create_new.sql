-- Version 1.0
-- Creates (or updates) entry in database

INSERT INTO view_state (guild_id, channel_id, message_id, state, view_name, creation_date)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (guild_id, channel_id, message_id)
DO UPDATE SET
    state = EXCLUDED.state;
