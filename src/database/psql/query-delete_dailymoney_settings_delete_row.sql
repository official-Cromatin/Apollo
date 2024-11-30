-- Version 1.0
-- Removes the matching row from the 'dailymoney_settings_delete' table

DELETE FROM dailymoney_settings_delete
WHERE message_id = $1