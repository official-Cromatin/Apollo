-- Version 1.0
-- Updates the current_page of the selected ranks message

UPDATE btn_ranks
SET current_page = $1
WHERE message_id = $2
