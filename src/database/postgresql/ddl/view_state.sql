CREATE TYPE "view_name" AS ENUM (
    'leaderboard'
);

CREATE TABLE "view_state" (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    channel_id BIGINT,
    message_id BIGINT,
    data JSON,
    view_name view_name,
    timeout INTEGER,
    active BOOLEAN,
    creation_date TIMESTAMP WITH TIME ZONE,
    last_loaded TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE,
    UNIQUE (guild_id, channel_id, message_id)
);
