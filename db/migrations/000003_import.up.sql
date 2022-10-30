BEGIN;

COPY application
FROM '/clientdata/shit3.csv' -- noqa
DELIMITER '$'
CSV HEADER;

COMMIT;
