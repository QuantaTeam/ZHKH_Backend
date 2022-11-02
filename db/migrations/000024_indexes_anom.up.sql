BEGIN;

CREATE INDEX is_anomaly_idx ON application(is_anomaly);

COMMIT;
