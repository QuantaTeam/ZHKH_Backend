BEGIN;

COPY application
FROM '/clientdata/hackfull.csv' -- noqa
DELIMITER '$'
CSV HEADER;

COMMIT;
