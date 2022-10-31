BEGIN;

ALTER TABLE application
DROP COLUMN applicant_id;

COMMIT;
