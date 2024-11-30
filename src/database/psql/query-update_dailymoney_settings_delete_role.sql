-- Version 1.O
-- Update row in 'dailymoney_settings_delete' table, to match the RoleSelectMenu interaction

UPDATE dailymoney_settings_delete
SET role_id = $1
WHERE message_id = $2