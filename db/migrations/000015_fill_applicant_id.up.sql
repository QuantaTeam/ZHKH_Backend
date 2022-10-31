BEGIN;

UPDATE application
SET applicant_id = CONCAT("Адрес проблемы", "Подъезд", "Этаж", "Квартира");

COMMIT;
