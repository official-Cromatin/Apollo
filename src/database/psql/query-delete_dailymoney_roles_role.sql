-- Version 1.0
-- Delete matching row in 'dailymoney_roles' table to remove matching role from dailymoney roles

DELETE FROM dailymoney_roles
WHERE role_id = $1
