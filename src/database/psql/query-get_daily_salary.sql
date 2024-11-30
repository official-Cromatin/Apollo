-- Version 1.0
-- Returns the daily salary determined by the role of the user with the highest priority in the 'dailymoney_roles' table

SELECT daily_salary FROM public.dailymoney_roles
WHERE guild_id = $1
AND role_id = ANY($2)
ORDER BY role_priority DESC, daily_salary DESC
LIMIT 1