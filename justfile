up-backend:
    pdm run uvicorn sarah.main:app --reload

up-db:
    docker-compose -f docker-compose.yml -f docker-compose.local.yml --profile db up --build

set dotenv-load
pgcli:
    pgcli postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB
