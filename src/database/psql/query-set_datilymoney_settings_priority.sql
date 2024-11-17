-- Version 1.0
-- Updates the priority for the specified role setting view

UPDATE dailymoney_add_settings
SET priority = $1
WHERE message_id = $2