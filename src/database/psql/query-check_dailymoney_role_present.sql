-- Version 1.0
-- Returns rows matching guild and role id to check the presence of a certain role

SELECT role_id
FROM dailymoney_roles
WHERE guild_id = $1
AND role_id = $2