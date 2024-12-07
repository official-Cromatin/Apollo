-- Version 1.0
-- Inserts a row into the btn_ranks table to store informations about the ranks view message

INSERT INTO btn_ranks ("message_id", "current_page")
VALUES ($1, $2)