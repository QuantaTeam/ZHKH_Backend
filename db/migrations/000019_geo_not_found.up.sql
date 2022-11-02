BEGIN;

ALTER TABLE application ADD COLUMN geo_not_found BOOLEAN;

COMMIT;
