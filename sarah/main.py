import typing

import fastapi
import structlog
from fastapi.middleware.cors import CORSMiddleware

from sarah import api, config

origins = [
    "*",
    "https://hack.barklan.com",
    "http://localhost",
]


shared_processors: list[typing.Any] = []

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api.router, prefix=config.settings.API_STR)
