-- Version 1.0
-- Creates a new entry in the "pick message" table, to link to the pick money message

INSERT INTO pick_money (guild_id, channel_id, message_id, amount)
VALUES ($1, $2, $3, $4)