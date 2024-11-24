-- Version 1.0
-- Deletes the specified row of the dailymoney_settings table

DELETE FROM dailymoney_settings
WHERE message_id = $1