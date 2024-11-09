-- Version 1.0
-- Stores the balance of an user, per server

CREATE TABLE "money" (
	"guild_id" INTEGER NOT NULL,
	"user_id" INTEGER NOT NULL,
	"balance" INTEGER NOT NULL DEFAULT 0,
	"last_claimed" DATE,
	PRIMARY KEY("guild_id", "user_id")
);
