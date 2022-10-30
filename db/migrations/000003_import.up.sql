BEGIN;

COPY application
FROM '/clientdata/sample_500_000.csv' -- noqa
DELIMITER '$'
CSV HEADER;

COMMIT;
