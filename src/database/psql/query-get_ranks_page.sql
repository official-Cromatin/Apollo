-- Version 1.0
-- Selects the current_page for a specific ranks view message

SELECT current_page
FROM btn_ranks
WHERE message_id = $1