up-backend:
    pdm run uvicorn sarah.main:app --reload

up-db:
    docker-compose -f docker-compose.yml -f docker-compose.local.yml --profile db up --build

set dotenv-load
pgcli:
    pgcli postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB

db-makemigrations target:
    docker run -v "$(pwd)"/db/migrations:/migrations -u 1000:1000 --network host migrate/migrate \
    create -ext sql -dir /migrations -seq {{target}}

db-migrate:
    docker run -v "$(pwd)"/db/migrations:/migrations \
    -v "$(pwd)"/db/data:/data \
    -u 1000:1000 --network host migrate/migrate \
    -database postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB?sslmode=disable -path /migrations up

db-force target:
    docker run -v "$(pwd)"/db/migrations:/migrations --network host migrate/migrate \
    -database postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB?sslmode=disable -path /migrations force {{target}}
