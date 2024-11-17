-- Version 1.0
-- Load roles, thier priority and daily salary for a certain guild

SELECT role_priority, role_id, daily_salary 
FROM dailymoney_roles
WHERE guild_id = $1