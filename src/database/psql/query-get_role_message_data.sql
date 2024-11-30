-- Version 1.0
-- Get the data to update the message

SELECT role_id, priority, daily_salary, main_message_id, edit_mode
FROM dailymoney_settings_edit
WHERE message_id = $1