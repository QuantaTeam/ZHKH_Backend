begin;

CREATE TABLE moscow_geo(
    external_id bigint,
    address TEXT,
    short_address TEXT,
    x_geo numeric(8, 6),
    y_geo numeric(8, 6)
);

commit;
