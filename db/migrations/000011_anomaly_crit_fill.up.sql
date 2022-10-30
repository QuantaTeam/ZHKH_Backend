BEGIN;

COPY anomaly_criteria
FROM '/clientdata/anomaly_criteria.csv' -- noqa
DELIMITER ','
CSV HEADER;

COMMIT;

