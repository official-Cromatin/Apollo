-- Version 1.0
-- Updates the values for the specified dailymoney role

UPDATE dailymoney_roles
SET role_priority = $1, 
    daily_salary = $2
WHERE role_id = $3
