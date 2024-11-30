-- Version 1.0
-- Stores a timestamp, equivalent to the time the last time the user has picked up his dailymoney

CREATE TABLE "dailymoney_record" (
	"user_id" BIGINT NOT NULL,
	"last_pickup" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("user_id")
)