BEGIN;

COPY restricted_repeated_applications
FROM '/clientdata/restricted_repeated_applications.csv' -- noqa
DELIMITER ','
CSV HEADER;

COMMIT;
