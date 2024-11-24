-- Version 1.0
-- Updates the row containing the settings for the edit role view, using data saved for a certain dailymoney role

UPDATE dailymoney_settings
SET priority = subquery.role_priority,
    daily_salary = subquery.daily_salary
FROM (
    SELECT role_priority, daily_salary
    FROM dailymoney_roles
    WHERE role_id = $1
    ) AS subquery
WHERE dailymoney_settings.message_id = $2;