BEGIN;

CREATE TABLE moscow_geo(
    external_id BIGINT,
    address TEXT,
    short_address TEXT,
    x_geo NUMERIC(8, 6),
    y_geo NUMERIC(8, 6)
);

COMMIT;
