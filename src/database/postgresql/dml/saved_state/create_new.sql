-- Version 2.0
-- Creates (or updates) entry in database

INSERT INTO view_state (guild_id, channel_id, message_id, data, view_name, timeout, active, creation_date, last_loaded, last_updated)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
ON CONFLICT (guild_id, channel_id, message_id)
DO UPDATE SET
    data = EXCLUDED.data,
    last_updated = EXCLUDED.last_updated
RETURNING id;
