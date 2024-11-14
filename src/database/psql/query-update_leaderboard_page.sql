-- Version 1.0
-- Update the current page, to match the content of the message

UPDATE btn_leaderboard
SET current_page = $1
WHERE message_id = $2