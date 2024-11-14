-- Version 1.0
-- Stores data to handle an button interaction event, in order to scroll to another page

CREATE TABLE "btn_leaderboard" (
	"message_id" BIGINT NOT NULL,
	"current_page" SMALLINT NOT NULL,
	"expiration" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("message_id")
)