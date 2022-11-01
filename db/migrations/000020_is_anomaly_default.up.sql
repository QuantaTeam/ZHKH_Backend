begin;

ALTER TABLE application ALTER COLUMN is_anomaly SET DEFAULT false;
ALTER TABLE application ALTER COLUMN is_anomaly SET NOT NULL;

commit;
