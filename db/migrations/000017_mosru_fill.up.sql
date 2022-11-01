begin;

COPY "moscow_geo"
FROM '/clientdata/mosru.csv' -- noqa
DELIMITER '$'
CSV HEADER;

commit;
