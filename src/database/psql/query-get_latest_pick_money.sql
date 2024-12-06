-- Version 1.0
-- Returns the message_id aswell as the value of the lastest pick_money message in the specified channel, deletes the row if existant

WITH deleted_row AS (
    SELECT message_id, amount
    FROM pick_money
    WHERE channel_id = $1
    ORDER BY creation DESC
    LIMIT 1
)
DELETE FROM pick_money
WHERE message_id IN (SELECT message_id FROM deleted_row)
RETURNING message_id, amount;