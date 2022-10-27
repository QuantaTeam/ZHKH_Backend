BEGIN;

CREATE FUNCTION application_creation_timestamp(APPLICATION)
RETURNS TIMESTAMP WITH TIME ZONE
IMMUTABLE
LANGUAGE SQL AS $$
select TO_TIMESTAMP($1."Дата создания заявки в формате Timezo", 'YYYY-MM-DD HH24:MI:ss.USTZH')
$$;

CREATE FUNCTION application_closure_timestamp(APPLICATION)
RETURNS TIMESTAMP WITH TIME ZONE
IMMUTABLE
LANGUAGE SQL AS $$
select TO_TIMESTAMP($1."Дата закрытия", 'YYYY-MM-DD HH24:MI:ss.USTZH')
$$;

COMMIT;
