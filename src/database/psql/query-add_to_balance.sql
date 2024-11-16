-- Version 1.0
-- Adds a specified amount to a specified user

UPDATE money
SET balance = balance + $1
WHERE user_id = $2