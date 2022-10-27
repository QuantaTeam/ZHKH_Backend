import fastapi
import structlog

from sarah import api, config

shared_processors = []

if config.settings.DEBUG:
    processors = shared_processors + [
        structlog.dev.ConsoleRenderer(),
    ]
else:
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]

structlog.configure(processors)


logger = structlog.get_logger()

app = fastapi.FastAPI(
    title=config.settings.PROJECT_NAME,
    debug=config.settings.DEBUG,
)


app.include_router(api.router, prefix=config.settings.API_STR)
