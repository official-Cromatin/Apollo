-- Version 1.0
-- Stores data about the ranks view to process interactions

CREATE TABLE "btn_ranks" (
    "message_id" BIGINT,
    "current_page" SMALLINT,
    "creation" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("message_id")
)
