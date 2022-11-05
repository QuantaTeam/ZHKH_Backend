#!/bin/bash

set -e

export DOCKER_BUILDKIT=1
export SSH_SERVER_NAME=sbermain
export STACK_NAME=hack
export PROJECT_PATH=/home/docker/hack
export REGISTRY_USERNAME="${REGISTRY_USERNAME?Variable not set}"
export REGISTRY_PASSWORD="${REGISTRY_PASSWORD?Variable not set}"
export DOCKER_REGISTRY="${DOCKER_REGISTRY?Variable not set}"
export DOCKER_IMAGE_PREFIX="${DOCKER_IMAGE_PREFIX?Variable not set}"

docker login -u "${REGISTRY_USERNAME}" -p "${REGISTRY_PASSWORD}" "${DOCKER_REGISTRY}"

docker-compose build #--parallel
docker-compose push

# note: docker compose v2 has problems
# (echo -e "version: '3.9'\n";  docker compose -f docker-compose.yml config) > docker-stack.yml
just compose-config

ssh -tt -o StrictHostKeyChecking=no "${SSH_SERVER_NAME}" "mkdir -p ${PROJECT_PATH}/environment"
ssh -tt -o StrictHostKeyChecking=no "${SSH_SERVER_NAME}" "mkdir -p ${PROJECT_PATH}/frontend"

scp docker-stack.yml .env "${SSH_SERVER_NAME}:${PROJECT_PATH}/"
scp -r environment "${SSH_SERVER_NAME}:${PROJECT_PATH}"
rsync -azvc --delete db "${SSH_SERVER_NAME}:${PROJECT_PATH}"

ssh -tt -o StrictHostKeyChecking=no "${SSH_SERVER_NAME}" \
	"docker login -u ${REGISTRY_USERNAME} -p ${REGISTRY_PASSWORD} ${DOCKER_REGISTRY} \
&& cd ${PROJECT_PATH} && docker stack deploy -c docker-stack.yml --with-registry-auth $STACK_NAME"
