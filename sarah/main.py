import typing
from urllib.parse import urlencode

import fastapi
import structlog
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from starlette.requests import Request
from starlette.responses import Response

from sarah import api, config

origins = [
    "*",
    "https://hack.barklan.com",
    "http://localhost",
]


def dict_to_string(mapping: dict, ignore: list[str]) -> str:
    string_list = []
    for key, value in mapping.items():
        if key not in ignore:
            string_list.append(f"{key}: {value}")
    return ";".join(string_list)


def cache_key_builder(
    func,
    namespace: typing.Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    actual_kwargs = kwargs["kwargs"]
    kwargs_string = dict_to_string(actual_kwargs, ["db", "log"])
    cache_key = (
        f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{kwargs_string}"
    )
    return cache_key


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


@app.middleware("http")
async def flatten_query_string_lists(request: Request, call_next):

    flattened = []
    for key, value in request.query_params.multi_items():
        flattened.extend((key, entry) for entry in value.split(","))

    request.scope["query_string"] = urlencode(flattened, doseq=True).encode("utf-8")

    return await call_next(request)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        f"redis://{config.settings.REDIS_SERVER}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(
        RedisBackend(redis), prefix="fastapi-cache", key_builder=cache_key_builder
    )


app.include_router(
    api.router,
    prefix=config.settings.API_STR,
)
