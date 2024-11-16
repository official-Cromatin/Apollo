-- Version 1.0
-- Updates the 'last_pickup' value to the current time

UPDATE dailymoney_record
SET last_pickup = CURRENT_TIMESTAMP
WHERE user_id = $1