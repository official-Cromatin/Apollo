-- Version 1.0
-- Updates the field in the row to match the reflected data in the config message

UPDATE channel_experience_settings
SET default_multiplier = $1,
    minimum_threshold = $2,
    maximum_experience = $3
WHERE channel_id = $4
