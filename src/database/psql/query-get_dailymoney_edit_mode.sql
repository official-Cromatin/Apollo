-- Version 1.0
-- Get the edit mode for the specified view

SELECT edit_mode
FROM dailymoney_settings
WHERE message_id = $1
