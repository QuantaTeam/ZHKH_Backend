BEGIN;

CREATE TABLE application ( -- noqa: disable=L057
    "Корневой ИД заявки" TEXT,
    "ИД версии заявки" TEXT,
    "Номер заявки" TEXT,
    "Уникальный номер обращения ГУ (mos.ru)" TEXT,
    "Дата создания заявки в формате Timezone" TEXT,
    "Дата начала действия версии заявки в формате Timezone" TEXT,
    "Наименование источника поступления заявки" TEXT,
    "Код источника поступления заявки" TEXT,
    "Имя создателя заявки" TEXT,
    "Признак инцидента" TEXT,
    "Корневой идентификатор материнской заявки" TEXT,
    "Номер материнской заявки" TEXT,
    "Пользователь, внесший последнее изменение" TEXT,
    "Роль организации пользователя" TEXT,
    "Комментарии" TEXT,
    "Наименование категории дефекта" TEXT,
    "Корневой идентификатор категории дефекта" TEXT,
    "Код категории дефекта" TEXT,
    "Наименование дефекта" TEXT,
    "Краткое наименование дефекта" TEXT,
    "Идентификатор дефекта" TEXT,
    "Код дефекта" TEXT,
    "Признак дефекта возврата на доработку" TEXT,
    "Описание" TEXT,
    "Наличие у заявителя вопроса" TEXT,
    "Наименование категории срочности: Аварийная, Обычная" TEXT,
    "Код категории срочности" TEXT,
    "Наименование округа" TEXT,
    "Код округа" TEXT,
    "Наименование района" TEXT,
    "Код района" TEXT,
    "Адрес проблемы" TEXT,
    "УНОМ" TEXT,
    "Подъезд" TEXT,
    "Этаж" TEXT,
    "Квартира" TEXT,
    "ОДС (номер объединенной диспетчерской службы)" TEXT,
    "Наименование управляющей компании" TEXT,
    "Наименование обслуживавшей организации (исполнителя)" TEXT,
    "Идентификатор организации-исполнителя" TEXT,
    "ИНН организации-исполнителя" TEXT,
    "Наименование статуса заявки" TEXT,
    "Код статуса заявки" TEXT,
    "Наименование причины отказа исполнителя" TEXT,
    "Идентификатор причины отказа исполнителя" TEXT,
    "Наименование причины отказа Организации-исполнителя" TEXT,
    "Идентификатор причины отказа Организации-исполнителя" TEXT,
    "Вид выполненных работ" TEXT,
    "Идентификатор корневой версии вида выполненных работ" TEXT,
    "Израсходованный материал" TEXT,
    "Наименование охранных мероприятий" TEXT,
    "Идентификатор корневой версии охранных мероприятий" TEXT,
    "Результативность" TEXT,
    "Код результативности" TEXT,
    "Кол-во возвратов на доработку" TEXT,
    "Дата последнего возврата на доработку" TEXT,
    "Признак нахождения на доработке" TEXT,
    "Признак “Оповещен”" TEXT,
    "Дата закрытия" TEXT,
    "Желаемое время с" TEXT,
    "Желаемое время до" TEXT,
    "Дата отзыва/оценки" TEXT,
    "Отзыв" TEXT,
    "Оценка качества выполнения работ" TEXT,
    "Код оценки качества выполнения ра" TEXT,
    "Наименование категории платности" TEXT,
    "Код категории платности" TEXT,
    "Признак оплаты картой" TEXT
);

COMMIT;
