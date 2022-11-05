BEGIN;

UPDATE application SET
    compound = "Наименование категории дефекта" || "Наименование дефекта" || "Наименование округа" || "Адрес проблемы" || "Наименование района" || "Код района" || "Код округа" || "Наименование управляющей компани" || "Наименование обслуживавшей орган";

COMMIT;