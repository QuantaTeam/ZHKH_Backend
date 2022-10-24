import fastapi
import structlog

from sarah import api, config

logger = structlog.get_logger()

app = fastapi.FastAPI(
    title=config.settings.PROJECT_NAME,
    debug=config.settings.DEBUG,
)


app.include_router(api.router, prefix=config.settings.API_STR)
