BEGIN;

ALTER TABLE application ADD COLUMN timestamp_start TIMESTAMP WITH TIME ZONE;
ALTER TABLE application ADD COLUMN timestamp_end TIMESTAMP WITH TIME ZONE;

COMMIT;
