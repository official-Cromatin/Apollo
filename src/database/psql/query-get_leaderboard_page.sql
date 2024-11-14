-- Version 1.0
-- Get the current page for a certain leaderboard view

SELECT current_page
FROM btn_leaderboard
WHERE message_id = $1