-- Version 1.0
-- Substracts a specified amount from a specified user

UPDATE money
SET balance = balance - $1
WHERE guild_id = $2
AND user_id = $3