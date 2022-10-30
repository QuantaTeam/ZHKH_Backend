BEGIN;

COPY short_defects
FROM '/clientdata/short_defects.csv' -- noqa
DELIMITER '$'
CSV HEADER;

COMMIT;
