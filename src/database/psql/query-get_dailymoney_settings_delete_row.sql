-- Version 1.0
-- Selects the 'role_id' for the matching row of the 'dailymoney_settings_delete' table

SELECT role_id, main_message_id
FROM dailymoney_settings_delete
WHERE message_id = $1