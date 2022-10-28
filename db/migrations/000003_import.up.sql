BEGIN;

COPY application
FROM '/clientdata/sample10000dollar.csv' -- noqa
DELIMITER '$'
CSV;

COMMIT;
