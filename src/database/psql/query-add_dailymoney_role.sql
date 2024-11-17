-- Version 1.0
-- Adds an dailymoney role to the set of roles that define how much money an user earns

INSERT INTO dailymoney_roles (guild_id, role_priority, role_id, daily_salary)
VALUES ($1, $2, $3, $4)