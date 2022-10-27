BEGIN;
CREATE TABLE restricted_repeated_applications( -- noqa: disable=L057
    "Идентификат" TEXT,
    "Корневой идентификат" TEXT,
    "Наименование" TEXT,
    "Категория" TEXT,
    "Повторное срок, часов" TEXT,
    "Повторное локация" TEXT
);
COMMIT;
