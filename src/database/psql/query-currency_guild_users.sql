-- Version 1.0
-- Gets the number of user, who have ever owned money on a certain guild
SELECT COUNT(*) 
FROM money 
WHERE guild_id = $1;