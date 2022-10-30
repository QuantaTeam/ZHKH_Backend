BEGIN;
CREATE TABLE anomaly_criteria( -- noqa: disable=L057
    "Идентификатор" TEXT,
    "Корневой идентификатор" TEXT,
    "Наименование" TEXT,
    "Категория" TEXT,
    "Повторное срок, часов" TEXT,
    "Повторное локация" TEXT
);
COMMIT;
