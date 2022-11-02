BEGIN;

CREATE INDEX timestamp_index ON application(timestamp_start);

COMMIT;
