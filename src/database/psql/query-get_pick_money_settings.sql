-- Version 1.0
-- Selects the applied settings regarding random apperance of pick money

SELECT min_amount, max_amount, probability
FROM channel_pick_money
WHERE channel_id = $1