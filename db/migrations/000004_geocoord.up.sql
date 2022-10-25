BEGIN;

ALTER TABLE application ADD COLUMN geo_coordinates TEXT;

COMMIT;
