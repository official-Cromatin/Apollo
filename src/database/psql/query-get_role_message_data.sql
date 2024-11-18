-- Version 1.0
-- Get the data to update the message

SELECT role_id, priority, daily_salary, main_message_id
FROM dailymoney_add_settings
WHERE message_id = $1