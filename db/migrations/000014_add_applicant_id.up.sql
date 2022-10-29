BEGIN;

ALTER TABLE application
ADD COLUMN applicant_id text;

COMMIT;
