-- Version 1.0
-- Deletes the specified row of the dailymoney_add_settings table

DELETE FROM dailymoney_add_settings
WHERE message_id = $1