-- Version 2.0
-- Creates (or updates) entry in database

INSERT INTO view_state (guild_id, channel_id, message_id, state, view_name, timeout, creation_date, last_loaded, last_updated)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
ON CONFLICT (guild_id, channel_id, message_id)
DO UPDATE SET
    state = EXCLUDED.state,
    last_updated = EXCLUDED.last_updated
RETURNING id;
