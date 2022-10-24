FROM python:3.10 AS builder

ENV PDM_USE_VENV=false

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /project/
COPY sarah/ /project/sarah

WORKDIR /project
RUN --mount=type=cache,target=/project/pkgs \
    pdm install --prod --no-lock --no-editable

FROM python:3.10

ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.10/lib /project/pkgs
COPY gunicorn_conf.py /project/

CMD ["python", "-m", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/project/gunicorn_conf.py", "sarah.main:app"]
