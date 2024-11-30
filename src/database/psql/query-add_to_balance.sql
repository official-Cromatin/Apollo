-- Version 2.0
-- Adds a specified amount to a specified user

INSERT INTO money (guild_id, user_id, balance)
VALUES ($1, $2, $3)
ON CONFLICT (guild_id, user_id)
DO UPDATE SET balance = money.balance + $3
WHERE money.guild_id = $1
AND money.user_id = $2