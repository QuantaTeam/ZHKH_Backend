begin;

update application
set timestamp_start = TO_TIMESTAMP("Дата создания заявки в формате Timezo", 'YYYY-MM-DD HH24:MI:ss.USTZH');

commit;
