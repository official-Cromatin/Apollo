-- Version 1.0
-- Querys and returns the last time a specified user, has picked up his dailymoney

SELECT last_pickup
FROM dailymoney_record
WHERE user_id = $1