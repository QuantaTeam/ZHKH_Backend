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

deploy-direct:
    #!/usr/bin/env bash
    # . .env
    # export REGISTRY_PASSWORD REGISTRY_USERNAME DOCKER_IMAGE_PREFIX DOCKER_REGISTRY
    echo "$DOCKER_REGISTRY"
    bash scripts/directswarm.sh

compose-config:
    #!/usr/bin/env bash
    docker run --rm -it -v "$(pwd)":/data barklan/docker_and_compose:1.2.0 docker-compose -v
    (echo -e "version: '3.9'\n"; \
    docker run --rm -it -v "$(pwd)":/data -w /data \
    -e DOCKER_IMAGE_PREFIX="${DOCKER_IMAGE_PREFIX}" \
    -e PROJECT_PATH="${PROJECT_PATH}" \
    barklan/docker_and_compose:1.2.0 docker-compose -f /data/docker-compose.yml config) > docker-stack.yml
