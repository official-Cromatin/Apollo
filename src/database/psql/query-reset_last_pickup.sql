-- Version 2.0
-- Updates the 'last_pickup' value to the current time, or if not found, inserts a new row

INSERT INTO dailymoney_record (user_id)
VALUES ($1)
ON CONFLICT (user_id)
DO UPDATE SET last_pickup = CURRENT_TIMESTAMP;