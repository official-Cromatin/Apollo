-- Version 1.0
-- Updates the daily salary for the specified role setting view

UPDATE dailymoney_add_settings
SET daily_salary = $1
WHERE message_id = $2