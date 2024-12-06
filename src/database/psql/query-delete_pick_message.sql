-- Version 1.0
-- Removes the row from the "pick_money" table after is has expired or got collected

DELETE FROM pick_money
WHERE message_id = $1
