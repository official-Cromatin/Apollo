-- Version 1.0
-- Updates the role for the specified role setting view

UPDATE dailymoney_settings
SET role_id = $1
WHERE message_id = $2