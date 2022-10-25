BEGIN;

ALTER TABLE application DROP COLUMN is_anomaly;

COMMIT;
