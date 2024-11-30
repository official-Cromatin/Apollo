-- Version 1.0
-- Deletes the specified row of the dailymoney_settings_edit table

DELETE FROM dailymoney_settings_edit
WHERE message_id = $1