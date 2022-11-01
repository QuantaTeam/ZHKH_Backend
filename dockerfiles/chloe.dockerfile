ARG DOCKER_IMAGE_PREFIX=
FROM ${DOCKER_IMAGE_PREFIX}python:3.10 AS builder

ENV PDM_USE_VENV=false

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /project/
COPY sarah/ /project/sarah

WORKDIR /project
RUN --mount=type=cache,target=/project/pkgs \
    pdm install --prod --no-lock --no-editable

FROM ${DOCKER_IMAGE_PREFIX}python:3.10

ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.10/lib /project/pkgs

CMD ["python", "sarah/anomaly/reader.py"]