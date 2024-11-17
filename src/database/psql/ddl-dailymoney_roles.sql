-- Version 1.0
-- Creates a table to store dailymoney roles, per server, together with thier priority aswell as daily salary

CREATE TABLE "dailymoney_roles" (
    "guild_id" bigint NOT NULL,
    "role_priority" smallint NOT NULL,
    "role_id" bigint NOT NULL,
    "daily_salary" smallint NOT NULL,
    PRIMARY KEY("guild_id")
);