-- Version 1.0
-- Updates or inserts the provided settings regarding the gain of experience

INSERT INTO channel_experience (guild_id, channel_id, default_multiplier, minimum_threshold, maximum_experience)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (channel_id)
DO UPDATE SET default_multiplier = $3,
              minimum_threshold = $4,
              maximum_experience = $5