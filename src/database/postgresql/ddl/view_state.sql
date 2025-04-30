CREATE TYPE "view_name" AS ENUM (
    'leaderboard'
);

CREATE TABLE "view_state" (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    channel_id BIGINT,
    message_id BIGINT,
    state JSON,
    view_name view_name,
    creation_date TIMESTAMP WITH TIME ZONE
);
