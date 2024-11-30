-- Version 1.0
-- Insert row in 'dailymoney_settings_delete' table to store information about the 'delete role' view

INSERT INTO dailymoney_settings_delete (main_message_id, message_id)
VALUES ($1, $2)
