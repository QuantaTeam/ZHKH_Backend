BEGIN;

CREATE FUNCTION row_estimator(query TEXT) RETURNS BIGINT
LANGUAGE plpgsql AS
$$DECLARE
   plan jsonb;
BEGIN
   EXECUTE 'EXPLAIN (FORMAT JSON) ' || query INTO plan;

   RETURN (plan->0->'Plan'->>'Plan Rows')::bigint;
END;$$;

COMMIT;
