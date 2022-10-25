BEGIN;

COPY application
FROM '/clientdata/sample10000dollar.csv'
DELIMITER '$'
CSV;

COMMIT;
